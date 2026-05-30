import time
from typing import Iterator

import cv2

from camera.base import Frame


class VideoFileAdapter:
    def __init__(self, path: str):
        self._cap = cv2.VideoCapture(path)
        if not self._cap.isOpened():
            raise ValueError(f"Cannot open video file: {path}")
        self._fps = self._cap.get(cv2.CAP_PROP_FPS) or 25.0

    def frames(self) -> Iterator[Frame]:
        while True:
            ret, image = self._cap.read()
            if not ret:
                break
            yield Frame(image=image, timestamp=time.time())

    def release(self) -> None:
        self._cap.release()
