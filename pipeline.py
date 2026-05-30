from camera.base import CameraSource
from analysis.base import Analyzer
from alerts.logger import Logger


def run(source: CameraSource, analyzer: Analyzer, logger: Logger) -> None:
    try:
        for frame in source.frames():
            detections = analyzer.analyze(frame.image)
            for detection in detections:
                logger.log(detection)
    finally:
        source.release()
        logger.close()
