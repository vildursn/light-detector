import { Audio } from 'expo-av';
import type { Detection } from '../analysis/types';
import type { Config } from '../analysis/types';

interface TrackedLight {
  bearing: number;
  color: string;
  firstSeen: number;
  lastSeen: number;
  lastAlerted: number;
  confirmed: boolean;
}

// Mutable state — lives for the lifetime of the watch session
const tracked: TrackedLight[] = [];
let sound: Audio.Sound | null = null;

async function playBeep(): Promise<void> {
  try {
    if (sound) {
      await sound.stopAsync();
      await sound.unloadAsync();
    }
    const { sound: s } = await Audio.Sound.createAsync(
      // expo-av can play a bundled asset; use a system sound as fallback
      { uri: 'https://www.soundjay.com/buttons/beep-01a.mp3' },
      { shouldPlay: true },
    );
    sound = s;
  } catch {
    // non-fatal — alarm is best-effort
  }
}

export async function processDetections(
  detections: Detection[],
  config: Config,
): Promise<void> {
  const now = Date.now() / 1000;

  // mark all tracked lights as not seen this frame
  for (const t of tracked) {
    if (now - t.lastSeen > config.lightGoneAfterSeconds) {
      // will be pruned below
    }
  }

  for (const d of detections) {
    const existing = tracked.find(
      t => Math.abs(t.bearing - d.bearing) <= config.bearingTolerance && t.color === d.color,
    );

    if (existing) {
      existing.lastSeen = now;

      if (!existing.confirmed && now - existing.firstSeen >= config.confirmAfterSeconds) {
        existing.confirmed = true;
      }

      if (existing.confirmed && now - existing.lastAlerted >= config.alertCooldownSeconds) {
        existing.lastAlerted = now;
        await playBeep();
      }
    } else {
      tracked.push({
        bearing: d.bearing,
        color: d.color,
        firstSeen: now,
        lastSeen: now,
        lastAlerted: 0,
        confirmed: false,
      });
    }
  }

  // prune stale lights
  for (let i = tracked.length - 1; i >= 0; i--) {
    if (now - tracked[i].lastSeen > config.lightGoneAfterSeconds) {
      tracked.splice(i, 1);
    }
  }
}

export function resetTracker(): void {
  tracked.length = 0;
}
