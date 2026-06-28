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

## Phone camera

The web UI has a **Camera** button that lets any device with a browser use its own camera as the video source — frames are sent to the server for analysis and detections are overlaid live.

Works on Mac and Android over plain HTTP. iPhone requires HTTPS.

**iPhone via Tailscale (recommended):**

1. Install [Tailscale](https://tailscale.com) on Mac and iPhone, log in with the same account
2. Enable HTTPS at [login.tailscale.com/admin/dns](https://login.tailscale.com/admin/dns)
3. Generate a cert:
   ```bash
   tailscale cert $(tailscale status --json | python3 -c \
     "import sys,json; d=json.load(sys.stdin); print(d['Self']['DNSName'].rstrip('.'))")
   ```
4. Start the server with the cert:
   ```bash
   python3 main.py --web --ssl-cert <hostname>.crt --ssl-key <hostname>.key
   ```
5. Open `https://<hostname>:8000` on iPhone → tap **Camera**

**Quick test (requires internet):**
```bash
# Terminal 1
python3 main.py --web

# Terminal 2
ssh -R 80:localhost:8000 localhost.run
```

Opens a temporary `https://...localhost.run` URL — works on iPhone without any setup.

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
| Analysis | `Analyzer` | `OpenCVAnalyzer`, `YOLOAnalyzer` (optional) |
| Output | — | `Logger` (SQLite), `AudioAlarm`, web UI (FastAPI + WebSocket) |

Detections are logged to `detections.db`.

## Configuration

Edit `config.py`:

| Setting | Default | Description |
|---|---|---|
| `camera_fov` | `90.0` | Camera horizontal field of view in degrees |
| `heading_offset` | `0.0` | Degrees offset from bow (0 = camera points forward) |
| `brightness_threshold` | `200` | Pixel brightness cutoff (0–255) |
| `min_confidence` | `0.10` | Discard detections below this confidence |
| `confirm_after_seconds` | `2.0` | Seconds a light must be visible before alerting |
| `alert_cooldown_seconds` | `60.0` | Minimum seconds between re-alerts for the same light |
| `analyzer` | `"opencv"` | `"opencv"` or `"yolo"` |
