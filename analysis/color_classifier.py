import cv2
import numpy as np


def classify_color(roi: np.ndarray) -> str:
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
