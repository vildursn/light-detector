import time
from threading import Event
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
    pause_event: Optional[Event] = None,
    step_forward_event: Optional[Event] = None,
    step_back_event: Optional[Event] = None,
) -> None:
    try:
        for frame in source.frames():
            if pause_event is not None:
                while not pause_event.is_set():
                    if step_forward_event is not None and step_forward_event.is_set():
                        step_forward_event.clear()
                        break
                    if step_back_event is not None and step_back_event.is_set():
                        step_back_event.clear()
                        if hasattr(source, 'seek') and hasattr(source, 'current_pos'):
                            source.seek(source.current_pos() - 2)
                        break
                    time.sleep(0.02)

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
