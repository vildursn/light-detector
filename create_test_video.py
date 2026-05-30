import cv2
import numpy as np

WIDTH, HEIGHT = 1280, 720
FPS = 15
DURATION = 20  # seconds

# (center_x, center_y, color_bgr, start_frame, end_frame, label)
# Lights pop on briefly against a mostly dark background
LIGHTS = [
    (180,  360, (0,   0,   255),  30,  55, "red"),    # red,   left     — appears ~2s, gone by ~3.7s
    (1050, 300, (0,   255, 0  ),  90, 120, "green"),  # green, right    — appears ~6s, gone by ~8s
    (640,  380, (255, 255, 255), 165, 185, "white"),  # white, center   — appears ~11s, gone by ~12.3s
    (820,  310, (0,   0,   255), 210, 240, "red"),    # red,   right    — appears ~14s, gone by ~16s
    (300,  340, (0,   255, 0  ), 255, 270, "green"),  # green, left     — appears ~17s, gone by ~18s
]


def draw_light(frame: np.ndarray, cx: int, cy: int, color: tuple, frame_num: int) -> None:
    flicker = 0.88 + 0.12 * np.sin(frame_num * 0.9)
    # Glow layers (dim, large) then bright core — full 255 at center survives blur
    for radius, scale in [(20, 0.08), (12, 0.25), (6, 0.55), (3, 0.85)]:
        scaled = tuple(min(255, int(c * scale)) for c in color)
        cv2.circle(frame, (cx, cy), radius, scaled, -1)
    # Full-brightness core: will still be ~230+ after 3x3 blur
    bright = tuple(min(255, int(c * flicker)) for c in color)
    cv2.circle(frame, (cx, cy), 2, bright, -1)


def main() -> None:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter("test_video.mp4", fourcc, FPS, (WIDTH, HEIGHT))

    total_frames = DURATION * FPS
    rng = np.random.default_rng(42)

    for i in range(total_frames):
        frame = np.full((HEIGHT, WIDTH, 3), (8, 5, 5), dtype=np.uint8)

        # faint star noise
        stars = rng.integers(0, 8, (HEIGHT, WIDTH, 3), dtype=np.uint8)
        frame = cv2.add(frame, stars)

        for cx, cy, color, start, end, _label in LIGHTS:
            if start <= i < end:
                draw_light(frame, cx, cy, color, i)

        out.write(frame)

    out.release()
    print(f"Created test_video.mp4  ({DURATION}s, {FPS}fps, {total_frames} frames)")
    print("Lights (mostly dark — lights appear briefly):")
    for cx, cy, color, start, end, label in LIGHTS:
        bearing = (cx / WIDTH - 0.5) * 90
        t_start = start / FPS
        t_end = end / FPS
        print(f"  {label:6s}  bearing={bearing:+.1f}°  {t_start:.1f}s – {t_end:.1f}s")


if __name__ == "__main__":
    main()
