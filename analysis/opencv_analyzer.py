from typing import List

import cv2
import numpy as np

from analysis.base import Detection
from config import Config


class OpenCVAnalyzer:
    def __init__(self, config: Config):
        self._config = config

    def analyze(self, image: np.ndarray) -> List[Detection]:
        height, width = image.shape[:2]
        # Check each channel independently — colored lights (red, green) are dim in grayscale
        b, g, r = cv2.split(image)
        thresh = np.zeros((height, width), dtype=np.uint8)
        for ch in (b, g, r):
            blurred = cv2.GaussianBlur(ch, (3, 3), 0)
            _, t = cv2.threshold(blurred, self._config.brightness_threshold, 255, cv2.THRESH_BINARY)
            thresh = cv2.bitwise_or(thresh, t)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if not (self._config.min_blob_area <= area <= self._config.max_blob_area):
                continue

            x, y, w, h = cv2.boundingRect(contour)
            cx = x + w // 2
            bearing = (cx / width - 0.5) * self._config.camera_fov + self._config.heading_offset

            roi = image[y:y + h, x:x + w]
            color = self._classify_color(roi)
            confidence = min(area / 200.0, 1.0)

            detections.append(Detection(bearing=bearing, color=color, confidence=confidence, bbox=(x, y, w, h)))

        return detections

    def _classify_color(self, roi: np.ndarray) -> str:
        if roi.size == 0:
            return "unknown"
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        red1 = cv2.inRange(hsv, (0, 80, 80), (10, 255, 255))
        red2 = cv2.inRange(hsv, (160, 80, 80), (180, 255, 255))
        green = cv2.inRange(hsv, (40, 80, 80), (90, 255, 255))
        white = cv2.inRange(hsv, (0, 0, 180), (180, 50, 255))

        counts = {
            "red": cv2.countNonZero(red1) + cv2.countNonZero(red2),
            "green": cv2.countNonZero(green),
            "white": cv2.countNonZero(white),
        }
        best = max(counts, key=lambda k: counts[k])
        return best if counts[best] > 0 else "unknown"
