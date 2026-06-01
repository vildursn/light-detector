from typing import List

import cv2
import numpy as np

from analysis.base import Detection
from analysis.color_classifier import classify_color
from config import Config


class OpenCVAnalyzer:
    def __init__(self, config: Config):
        self._config = config

    def analyze(self, image: np.ndarray) -> List[Detection]:
        height, width = image.shape[:2]

        glare_mask = self._build_glare_mask(image)
        threshold = self._compute_threshold(image)

        b, g, r = cv2.split(image)
        thresh = np.zeros((height, width), dtype=np.uint8)
        for ch in (b, g, r):
            blurred = cv2.GaussianBlur(ch, (3, 3), 0)
            _, t = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY)
            thresh = cv2.bitwise_or(thresh, t)

        # suppress glare regions
        thresh = cv2.bitwise_and(thresh, cv2.bitwise_not(glare_mask))

        # morphological opening: removes isolated noise pixels, preserves real blobs
        if self._config.morph_open_size > 1:
            kernel = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE,
                (self._config.morph_open_size, self._config.morph_open_size),
            )
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if not (self._config.min_blob_area <= area <= self._config.max_blob_area):
                continue

            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter ** 2)
            if circularity < self._config.min_circularity:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            cx = x + w // 2
            bearing = (cx / width - 0.5) * self._config.camera_fov + self._config.heading_offset

            roi = image[y:y + h, x:x + w]
            color = classify_color(roi)
            confidence = min(area / 200.0, 1.0)

            detections.append(Detection(bearing=bearing, color=color, confidence=confidence, bbox=(x, y, w, h)))

        return detections

    def _compute_threshold(self, image: np.ndarray) -> int:
        if not self._config.adaptive_threshold:
            return self._config.brightness_threshold
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        background = float(np.median(gray))
        t = int(background) + self._config.adaptive_margin
        return max(self._config.min_threshold, min(self._config.max_threshold, t))

    def _build_glare_mask(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        if not self._config.glare_filter:
            return np.zeros((h, w), dtype=np.uint8)

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        _, v = cv2.split(hsv)[1], cv2.split(hsv)[2]
        _, blown = cv2.threshold(v, self._config.glare_value_min, 255, cv2.THRESH_BINARY)

        # keep only large blown-out blobs (glare), discard small ones (light cores)
        n, labels, stats, _ = cv2.connectedComponentsWithStats(blown, connectivity=8)
        glare = np.zeros((h, w), dtype=np.uint8)
        for i in range(1, n):
            if stats[i, cv2.CC_STAT_AREA] >= self._config.glare_min_area:
                glare[labels == i] = 255

        if self._config.glare_dilate_px > 0:
            r = self._config.glare_dilate_px
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
            glare = cv2.dilate(glare, kernel)

        return glare

