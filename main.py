import sys

from config import Config
from camera.video_file import VideoFileAdapter
from analysis.opencv_analyzer import OpenCVAnalyzer
from alerts.logger import Logger
from pipeline import run


def main() -> None:
    video_path = sys.argv[1] if len(sys.argv) > 1 else "test_video.mp4"
    config = Config()
    source = VideoFileAdapter(video_path)
    analyzer = OpenCVAnalyzer(config)
    logger = Logger()
    print(f"Running on: {video_path}  FOV={config.camera_fov}°  threshold={config.brightness_threshold}")
    run(source, analyzer, logger)
    print("Done.")


if __name__ == "__main__":
    main()
