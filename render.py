import cv2
import numpy as np

from analysis.base import Detection

_COLOR_MAP = {
    "red": (0, 0, 255),
    "green": (0, 220, 0),
    "white": (210, 210, 210),
    "unknown": (100, 100, 100),
}


def annotate(image: np.ndarray, detections: list) -> np.ndarray:
    frame = image.copy()
    for d in detections:
        x, y, w, h = d.bbox
        color = _COLOR_MAP.get(d.color, (100, 100, 100))
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        label = f"{d.color} {d.bearing:+.0f}°"
        cv2.putText(frame, label, (x, max(y - 6, 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
    return frame
