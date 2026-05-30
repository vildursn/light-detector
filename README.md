# light-detector

Autonomous night watch system for sailboats. Detects navigation lights (red, green, white) from a camera feed and raises an alarm. Runs on Raspberry Pi; web UI is accessible from any browser on the same local network.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

**Terminal only (video file):**
```bash
python3 main.py                        # uses test_video.mp4 by default
python3 main.py path/to/video.mp4
```

**Terminal only (webcam):**
```bash
python3 main.py --webcam
```

**Web UI (video file):**
```bash
python3 main.py --web
python3 main.py --web path/to/video.mp4
```

**Web UI (webcam):**
```bash
python3 main.py --web --webcam
```

Open `http://localhost:8000` in a browser. On the same local network, replace `localhost` with the machine's IP address (e.g. `http://192.168.1.42:8000`).

**Custom port:**
```bash
python3 main.py --web --port 9000
```

## Test video

Generate a 20-second test video with lights appearing briefly at various bearings:
```bash
python3 create_test_video.py
```

## Architecture

Three modular layers — any can be swapped independently:

| Layer | Protocol | Implementations |
|---|---|---|
| Camera | `CameraSource` | `VideoFileAdapter`, `WebcamAdapter` |
| Analysis | `Analyzer` | `OpenCVAnalyzer` (+ YOLOv8 planned) |
| Output | — | `Logger` (SQLite), audio alarm (planned) |

Detections are logged to `detections.db`.

## Configuration

Edit `config.py`:

| Setting | Default | Description |
|---|---|---|
| `camera_fov` | `90.0` | Camera horizontal field of view in degrees |
| `heading_offset` | `0.0` | Degrees offset from bow (0 = camera points forward) |
| `brightness_threshold` | `200` | Pixel brightness cutoff (0–255) |
| `analyzer` | `"opencv"` | `"opencv"` or `"yolo"` |
