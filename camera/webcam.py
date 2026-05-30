import time
from typing import Iterator

import cv2

from camera.base import Frame


class WebcamAdapter:
    def __init__(self, index: int = 0):
        self._cap = cv2.VideoCapture(index)
        if not self._cap.isOpened():
            raise ValueError(f"Cannot open webcam {index}")

    def frames(self) -> Iterator[Frame]:
        while True:
            ret, image = self._cap.read()
            if ret:
                yield Frame(image=image, timestamp=time.time())

    def release(self) -> None:
        self._cap.release()
