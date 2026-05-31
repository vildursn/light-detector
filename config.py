from dataclasses import dataclass


@dataclass
class Config:
    camera_fov: float = 90.0        # horizontal field of view in degrees
    heading_offset: float = 0.0     # degrees: 0 = camera points to bow
    brightness_threshold: int = 200  # used only when adaptive_threshold is False
    min_blob_area: int = 5
    max_blob_area: int = 5000
    analyzer: str = "opencv"        # "opencv" | "yolo"

    # Adaptive thresholding
    adaptive_threshold: bool = True
    adaptive_margin: int = 80       # required brightness above background median
    min_threshold: int = 120        # floor — keeps sensitivity in very dark scenes
    max_threshold: int = 245        # ceiling — avoids matching pure overexposure

    # Glare filtering
    glare_filter: bool = True
    glare_value_min: int = 252      # HSV-V cutoff for blown-out pixels
    glare_min_area: int = 300       # blobs larger than this are glare, not lights
    glare_dilate_px: int = 25       # expand glare mask to suppress halos
