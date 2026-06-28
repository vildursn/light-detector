import argparse

from config import Config
from camera.video_file import VideoFileAdapter
from analysis.opencv_analyzer import OpenCVAnalyzer
from analysis.yolo_analyzer import YOLOAnalyzer
from analysis.proxy import AnalyzerProxy
from alerts.logger import Logger
from alerts.tracker import LightTracker
from alerts.audio_alarm import AudioAlarm
from pipeline import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Sailboat night light detector")
    parser.add_argument("video", nargs="?", default="test_video.mp4", help="Video file path")
    parser.add_argument("--webcam", action="store_true", help="Use webcam instead of video file")
    parser.add_argument("--web", action="store_true", help="Start web UI")
    parser.add_argument("--port", type=int, default=8000, help="Web UI port (default 8000)")
    parser.add_argument("--no-loop", action="store_true", help="Play video file once instead of looping")
    parser.add_argument("--analyzer", choices=["opencv", "yolo"], default="opencv", help="Starting analyzer")
    args = parser.parse_args()

    config = Config()

    if args.webcam:
        from camera.webcam import WebcamAdapter
        source = WebcamAdapter()
        source_name = "webcam"
    else:
        source = VideoFileAdapter(args.video, loop=not args.no_loop)
        source_name = args.video

    opencv_analyzer = OpenCVAnalyzer(config)
    yolo_analyzer = YOLOAnalyzer(config) if YOLOAnalyzer.available else None

    initial = yolo_analyzer if (args.analyzer == "yolo" and yolo_analyzer) else opencv_analyzer
    proxy = AnalyzerProxy(initial)

    tracker = LightTracker(config)
    logger = Logger()
    alarm = AudioAlarm()

    if args.web:
        from web.server import run_web
        print(f"Source: {source_name}  →  http://0.0.0.0:{args.port}")
        if not YOLOAnalyzer.available:
            print("YOLO unavailable (pip install ultralytics to enable)")
        run_web(source, proxy, opencv_analyzer, yolo_analyzer, logger,
                tracker=tracker, min_confidence=config.min_confidence,
                is_live=args.webcam, port=args.port, alarm=alarm)
    else:
        print(f"Source: {source_name}  analyzer={proxy.name()}  min_conf={config.min_confidence}")
        run(source, proxy, logger, tracker=tracker, min_confidence=config.min_confidence, on_alert=alarm.alert)
        print("Done.")


if __name__ == "__main__":
    main()
