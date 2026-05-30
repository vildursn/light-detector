import argparse

from config import Config
from camera.video_file import VideoFileAdapter
from analysis.opencv_analyzer import OpenCVAnalyzer
from alerts.logger import Logger
from pipeline import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Sailboat night light detector")
    parser.add_argument("video", nargs="?", default="test_video.mp4", help="Video file path")
    parser.add_argument("--webcam", action="store_true", help="Use webcam instead of video file")
    parser.add_argument("--web", action="store_true", help="Start web UI")
    parser.add_argument("--port", type=int, default=8000, help="Web UI port (default 8000)")
    args = parser.parse_args()

    config = Config()

    if args.webcam:
        from camera.webcam import WebcamAdapter
        source = WebcamAdapter()
        source_name = "webcam"
    else:
        source = VideoFileAdapter(args.video)
        source_name = args.video

    analyzer = OpenCVAnalyzer(config)
    logger = Logger()

    if args.web:
        from web.server import run_web
        print(f"Source: {source_name}  →  http://0.0.0.0:{args.port}")
        run_web(source, analyzer, logger, port=args.port)
    else:
        print(f"Source: {source_name}  FOV={config.camera_fov}°  threshold={config.brightness_threshold}")
        run(source, analyzer, logger)
        print("Done.")


if __name__ == "__main__":
    main()
