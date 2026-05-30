import threading
from typing import List

import numpy as np

from analysis.base import Detection


class AnalyzerProxy:
    """Thread-safe wrapper that delegates to whichever analyzer is currently active."""

    def __init__(self, initial):
        self._current = initial
        self._lock = threading.Lock()

    def set(self, analyzer) -> None:
        with self._lock:
            self._current = analyzer

    def name(self) -> str:
        with self._lock:
            return type(self._current).__name__

    def analyze(self, image: np.ndarray) -> List[Detection]:
        with self._lock:
            analyzer = self._current
        return analyzer.analyze(image)
