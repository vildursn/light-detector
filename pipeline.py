from typing import Callable, Optional

from camera.base import CameraSource
from analysis.base import Analyzer
from alerts.logger import Logger


def run(
    source: CameraSource,
    analyzer: Analyzer,
    logger: Logger,
    on_frame: Optional[Callable] = None,
) -> None:
    try:
        for frame in source.frames():
            detections = analyzer.analyze(frame.image)
            for detection in detections:
                logger.log(detection)
            if on_frame is not None:
                on_frame(frame.image, detections)
    finally:
        source.release()
        logger.close()
