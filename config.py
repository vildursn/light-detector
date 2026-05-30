from dataclasses import dataclass


@dataclass
class Config:
    camera_fov: float = 90.0        # horizontal field of view in degrees
    heading_offset: float = 0.0     # degrees: 0 = camera points to bow
    brightness_threshold: int = 200  # 0-255, pixels brighter than this are candidates
    min_blob_area: int = 5
    max_blob_area: int = 5000
    analyzer: str = "opencv"        # "opencv" | "yolo"
