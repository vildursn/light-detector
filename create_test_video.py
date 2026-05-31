import cv2
import numpy as np

WIDTH, HEIGHT = 1280, 720
FPS = 15
DURATION = 35  # seconds

# (cx, cy, color_bgr, start_frame, end_frame, label)
LIGHTS = [
    (180,  360, (0,   0,   255),  45,  82,  "red"),    # ~3s – 5.5s,  left
    (1050, 300, (0,   255, 0  ), 135, 172,  "green"),  # ~9s – 11.5s, right
    (640,  400, (255, 255, 255), 255, 285,  "white"),  # ~17s – 19s,  center
    (820,  310, (0,   0,   255), 330, 367,  "red"),    # ~22s – 24.5s,right
    (300,  340, (0,   255, 0  ), 435, 465,  "green"),  # ~29s – 31s,  left
]

# Glare event: large blown-out patch t=13–15s — tests glare filter
GLARE = {"start": 195, "end": 225, "cx": 950, "cy": 220, "radius": 90}


def background(frame_num: int, rng: np.random.Generator) -> np.ndarray:
    # Slow ambient brightness variation (moon behind clouds feel)
    ambient = 12 + 8 * np.sin(frame_num * 0.018) + 4 * np.sin(frame_num * 0.041)

    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)

    # Sky: very dark, slightly bluer
    frame[:HEIGHT // 2, :] = [ambient * 0.55, ambient * 0.45, ambient * 0.7]

    # Sea: dark, greenish-grey, slightly brighter than sky
    frame[HEIGHT // 2:, :] = [ambient * 0.45, ambient * 0.5, ambient * 0.4]

    # Horizontal ripple bands on the water surface
    for band_y in range(HEIGHT // 2, HEIGHT, 18):
        phase = frame_num * 0.25 + band_y * 0.08
        brightness = 2.5 * np.sin(phase)
        y = band_y + int(3 * np.sin(frame_num * 0.18 + band_y * 0.04))
        if 0 <= y < HEIGHT:
            frame[y, :, 0] += brightness * 0.4
            frame[y, :, 1] += brightness * 0.45
            frame[y, :, 2] += brightness * 0.35

    # Occasional water reflection streak (moon / ambient light on water)
    if rng.random() < 0.12:
        ry = int(rng.integers(HEIGHT // 2 + 10, HEIGHT - 10))
        rx = int(rng.integers(50, WIDTH - 200))
        rw = int(rng.integers(40, 180))
        rb = float(rng.uniform(6, 18))
        frame[ry:ry + 2, rx:rx + rw, 0] += rb * 0.4
        frame[ry:ry + 2, rx:rx + rw, 1] += rb * 0.45
        frame[ry:ry + 2, rx:rx + rw, 2] += rb * 0.35

    # Random stars (top half only — occasional single bright pixels)
    n_stars = int(rng.integers(0, 6))
    for _ in range(n_stars):
        sx = int(rng.integers(0, WIDTH))
        sy = int(rng.integers(0, HEIGHT // 2))
        sb = float(rng.uniform(18, 45))
        frame[sy, sx] = [sb * 0.7, sb * 0.65, sb]

    # Gaussian noise
    frame += rng.normal(0, 2.5, (HEIGHT, WIDTH, 3))

    return np.clip(frame, 0, 255).astype(np.uint8)


def draw_glare(frame: np.ndarray, cx: int, cy: int, radius: int) -> None:
    # Blown-out sun-reflection patch — large, fully saturated white
    for r, val in [(radius, 160), (radius * 2 // 3, 220), (radius // 3, 255)]:
        cv2.circle(frame, (cx, cy), r, (val, val, val), -1)
    # Horizontal glare streak on water
    streak_y = cy + radius + 20
    if 0 <= streak_y < HEIGHT:
        cv2.ellipse(frame, (cx, streak_y), (radius * 2, radius // 3), 0, 0, 360, (200, 200, 200), -1)


def draw_light(frame: np.ndarray, cx: int, cy: int, color: tuple, frame_num: int) -> None:
    flicker = 0.88 + 0.12 * np.sin(frame_num * 0.9)
    for r, scale in [(20, 0.08), (12, 0.25), (6, 0.55), (3, 0.85)]:
        scaled = tuple(min(255, int(c * scale)) for c in color)
        cv2.circle(frame, (cx, cy), r, scaled, -1)
    bright = tuple(min(255, int(c * flicker)) for c in color)
    cv2.circle(frame, (cx, cy), 2, bright, -1)


def main() -> None:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter("test_video.mp4", fourcc, FPS, (WIDTH, HEIGHT))

    total_frames = DURATION * FPS
    rng = np.random.default_rng(42)

    for i in range(total_frames):
        frame = background(i, rng)

        if GLARE["start"] <= i < GLARE["end"]:
            draw_glare(frame, GLARE["cx"], GLARE["cy"], GLARE["radius"])

        for cx, cy, color, start, end, _label in LIGHTS:
            if start <= i < end:
                draw_light(frame, cx, cy, color, i)

        out.write(frame)

    out.release()
    print(f"Created test_video.mp4  ({DURATION}s, {FPS}fps, {total_frames} frames)")
    print(f"Glare event: {GLARE['start']/FPS:.1f}s – {GLARE['end']/FPS:.1f}s")
    print("Lights:")
    for cx, cy, color, start, end, label in LIGHTS:
        bearing = (cx / WIDTH - 0.5) * 90
        print(f"  {label:6s}  bearing={bearing:+.1f}°  {start/FPS:.1f}s – {end/FPS:.1f}s")


if __name__ == "__main__":
    main()
