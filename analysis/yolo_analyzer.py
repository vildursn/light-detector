from typing import List

import numpy as np

from analysis.base import Detection
from config import Config

try:
    from ultralytics import YOLO as _YOLO
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False


class YOLOAnalyzer:
    available: bool = _AVAILABLE

    def __init__(self, config: Config, model_path: str = "yolov8n.pt"):
        self._config = config
        self._model = _YOLO(model_path) if _AVAILABLE else None

    def analyze(self, image: np.ndarray) -> List[Detection]:
        if self._model is None:
            return []
        height, width = image.shape[:2]
        results = self._model(image, verbose=False)[0]
        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            w, h = x2 - x1, y2 - y1
            cx = x1 + w // 2
            bearing = (cx / width - 0.5) * self._config.camera_fov + self._config.heading_offset
            conf = float(box.conf[0])
            detections.append(Detection(bearing=bearing, color="unknown", confidence=conf, bbox=(x1, y1, w, h)))
        return detections
