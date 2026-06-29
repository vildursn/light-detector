import type { Detection, LightColor, Config } from './types';

// Runs as a Reanimated worklet on the camera thread.
// Input: RGB Uint8Array from vision-camera-resize-plugin (width x height x 3 bytes).
// Output: list of detections with bearing, color, confidence, bbox.

function rgbToHsv(r: number, g: number, b: number): [number, number, number] {
  'worklet';
  const rn = r / 255;
  const gn = g / 255;
  const bn = b / 255;
  const max = Math.max(rn, gn, bn);
  const min = Math.min(rn, gn, bn);
  const delta = max - min;

  let h = 0;
  if (delta > 0) {
    if (max === rn) h = 60 * (((gn - bn) / delta) % 6);
    else if (max === gn) h = 60 * ((bn - rn) / delta + 2);
    else h = 60 * ((rn - gn) / delta + 4);
    if (h < 0) h += 360;
  }

  const s = max === 0 ? 0 : delta / max;
  const v = max;
  return [h, s * 255, v * 255];
}

function classifyColor(h: number, s: number, v: number): LightColor {
  'worklet';
  if (v < 80) return 'unknown';
  if (s < 50 && v > 180) return 'white';
  if (s < 50) return 'unknown';
  if ((h <= 10 || h >= 160) && h <= 180) return 'red';
  if (h >= 40 && h <= 90) return 'green';
  return 'unknown';
}

function computeAdaptiveThreshold(
  data: Uint8Array,
  width: number,
  height: number,
  config: Config,
): number {
  'worklet';
  if (!config.adaptiveThreshold) return config.brightnessThreshold;

  // sample every 8th pixel for a fast median estimate
  const samples: number[] = [];
  const step = 8 * 3;
  for (let i = 0; i < data.length; i += step) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    samples.push((r + g + b) / 3);
  }
  samples.sort((a, b) => a - b);
  const median = samples[Math.floor(samples.length / 2)];
  const t = median + config.adaptiveMargin;
  return Math.max(config.minThreshold, Math.min(config.maxThreshold, t));
}

export function detectLights(
  data: Uint8Array,
  width: number,
  height: number,
  config: Config,
): Detection[] {
  'worklet';

  const threshold = computeAdaptiveThreshold(data, width, height, config);

  // Grid-based blob detection: 8x8 cells
  const cellSize = 8;
  const cols = Math.floor(width / cellSize);
  const rows = Math.floor(height / cellSize);

  // For each cell: is it bright? what color?
  const bright: boolean[] = new Array(cols * rows).fill(false);
  const cellH: number[] = new Array(cols * rows).fill(0);
  const cellS: number[] = new Array(cols * rows).fill(0);
  const cellV: number[] = new Array(cols * rows).fill(0);

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      let sumR = 0, sumG = 0, sumB = 0, count = 0;
      let anyBright = false;

      for (let dy = 0; dy < cellSize; dy++) {
        for (let dx = 0; dx < cellSize; dx++) {
          const px = (row * cellSize + dy) * width + (col * cellSize + dx);
          const i = px * 3;
          const r = data[i], g = data[i + 1], b = data[i + 2];
          if (r > threshold || g > threshold || b > threshold) anyBright = true;
          sumR += r; sumG += g; sumB += b; count++;
        }
      }

      const idx = row * cols + col;
      bright[idx] = anyBright;
      if (anyBright) {
        const [h, s, v] = rgbToHsv(sumR / count, sumG / count, sumB / count);
        cellH[idx] = h;
        cellS[idx] = s;
        cellV[idx] = v;
      }
    }
  }

  // Group adjacent bright cells (4-connectivity flood fill)
  const visited: boolean[] = new Array(cols * rows).fill(false);
  const detections: Detection[] = [];

  for (let start = 0; start < cols * rows; start++) {
    if (!bright[start] || visited[start]) continue;

    const stack = [start];
    const group: number[] = [];
    visited[start] = true;

    while (stack.length > 0) {
      const cur = stack.pop()!;
      group.push(cur);
      const r = Math.floor(cur / cols);
      const c = cur % cols;
      const neighbors = [
        r > 0 ? (r - 1) * cols + c : -1,
        r < rows - 1 ? (r + 1) * cols + c : -1,
        c > 0 ? r * cols + (c - 1) : -1,
        c < cols - 1 ? r * cols + (c + 1) : -1,
      ];
      for (const n of neighbors) {
        if (n >= 0 && bright[n] && !visited[n]) {
          visited[n] = true;
          stack.push(n);
        }
      }
    }

    // area in pixels²
    const area = group.length * cellSize * cellSize;
    if (area < config.minBlobArea || area > config.maxBlobArea) continue;

    // bounding box
    let minCol = cols, maxCol = 0, minRow = rows, maxRow = 0;
    let sumH = 0, sumS = 0, sumV = 0;
    for (const idx of group) {
      const gr = Math.floor(idx / cols);
      const gc = idx % cols;
      if (gc < minCol) minCol = gc;
      if (gc > maxCol) maxCol = gc;
      if (gr < minRow) minRow = gr;
      if (gr > maxRow) maxRow = gr;
      sumH += cellH[idx];
      sumS += cellS[idx];
      sumV += cellV[idx];
    }

    const avgH = sumH / group.length;
    const avgS = sumS / group.length;
    const avgV = sumV / group.length;
    const color = classifyColor(avgH, avgS, avgV);
    if (color === 'unknown') continue;

    const bboxX = minCol * cellSize;
    const bboxY = minRow * cellSize;
    const bboxW = (maxCol - minCol + 1) * cellSize;
    const bboxH = (maxRow - minRow + 1) * cellSize;
    const cx = bboxX + bboxW / 2;

    const bearing = (cx / width - 0.5) * config.cameraFov + config.headingOffset;
    const confidence = Math.min(area / 200, 1.0);

    detections.push({ bearing, color, confidence, bbox: { x: bboxX, y: bboxY, w: bboxW, h: bboxH } });
  }

  return detections;
}
