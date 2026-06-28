import threading

import numpy as np
import sounddevice as sd

_SAMPLE_RATE = 44100
_BEEP_DURATION = 0.15
_BEEP_GAP = 0.08
_BEEPS = 3

_FREQ = {
    "red": 440,
    "green": 880,
    "white": 660,
}


class AudioAlarm:
    def __init__(self, volume: float = 0.7):
        self._volume = volume

    def alert(self, light) -> None:
        freq = _FREQ.get(light.color, 660)
        threading.Thread(target=self._play, args=(freq,), daemon=True).start()

    def _play(self, freq: float) -> None:
        n = int(_SAMPLE_RATE * _BEEP_DURATION)
        gap = np.zeros(int(_SAMPLE_RATE * _BEEP_GAP), dtype=np.float32)
        t = np.linspace(0, _BEEP_DURATION, n, endpoint=False)
        beep = (self._volume * np.sin(2 * np.pi * freq * t)).astype(np.float32)
        signal = np.concatenate([np.concatenate([beep, gap]) for _ in range(_BEEPS)])
        sd.play(signal, _SAMPLE_RATE)
        sd.wait()
