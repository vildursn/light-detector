import time
from typing import Iterator

import cv2

from camera.base import Frame


class VideoFileAdapter:
    def __init__(self, path: str, loop: bool = False):
        self._path = path
        self._loop = loop
        self._cap = cv2.VideoCapture(path)
        if not self._cap.isOpened():
            raise ValueError(f"Cannot open video file: {path}")
        self._fps = self._cap.get(cv2.CAP_PROP_FPS) or 25.0

    def frames(self) -> Iterator[Frame]:
        frame_duration = 1.0 / self._fps
        while True:
            t0 = time.time()
            ret, image = self._cap.read()
            if not ret:
                if self._loop:
                    self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                break
            yield Frame(image=image, timestamp=t0)
            elapsed = time.time() - t0
            spare = frame_duration - elapsed
            if spare > 0:
                time.sleep(spare)

    def current_pos(self) -> int:
        return int(self._cap.get(cv2.CAP_PROP_POS_FRAMES))

    def seek(self, frame_num: int) -> None:
        total = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, min(frame_num, total - 1)))

    def release(self) -> None:
        self._cap.release()
