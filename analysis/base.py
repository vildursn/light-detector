from dataclasses import dataclass
from typing import Protocol, List
import numpy as np


@dataclass
class Detection:
    bearing: float
    color: str  # "red" | "green" | "white" | "unknown"
    confidence: float
    bbox: tuple  # (x, y, w, h)


class Analyzer(Protocol):
    def analyze(self, image: np.ndarray) -> List[Detection]: ...
