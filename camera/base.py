from dataclasses import dataclass
from typing import Iterator, Protocol
import numpy as np


@dataclass
class Frame:
    image: np.ndarray
    timestamp: float


class CameraSource(Protocol):
    def frames(self) -> Iterator[Frame]: ...
    def release(self) -> None: ...
