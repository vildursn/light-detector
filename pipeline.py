from typing import Callable, Optional

from camera.base import CameraSource
from analysis.base import Analyzer
from alerts.logger import Logger


def run(
    source: CameraSource,
    analyzer: Analyzer,
    logger: Logger,
    on_frame: Optional[Callable] = None,
    on_alert: Optional[Callable] = None,
    tracker=None,
    min_confidence: float = 0.0,
) -> None:
    try:
        for frame in source.frames():
            detections = analyzer.analyze(frame.image)

            if min_confidence > 0:
                detections = [d for d in detections if d.confidence >= min_confidence]

            if tracker is not None:
                confirmed = tracker.update(detections)
                for light in confirmed:
                    logger.log_event(light)
                    if on_alert is not None:
                        on_alert(light)
            else:
                for det in detections:
                    logger.log(det)

            if on_frame is not None:
                on_frame(frame.image, detections)
    finally:
        source.release()
        logger.close()
