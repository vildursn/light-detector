import asyncio
import json
import threading
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import cv2
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse

from render import annotate

_loop: asyncio.AbstractEventLoop | None = None


class _ConnectionManager:
    def __init__(self):
        self._connections: list[WebSocket] = []
        self._lock = threading.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        with self._lock:
            self._connections.append(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        with self._lock:
            try:
                self._connections.remove(ws)
            except ValueError:
                pass

    def _snapshot(self) -> list[WebSocket]:
        with self._lock:
            return list(self._connections)

    async def broadcast_bytes(self, data: bytes) -> None:
        dead = []
        for ws in self._snapshot():
            try:
                await ws.send_bytes(data)
            except Exception:
                dead.append(ws)
        with self._lock:
            for ws in dead:
                try:
                    self._connections.remove(ws)
                except ValueError:
                    pass

    async def broadcast_text(self, text: str) -> None:
        dead = []
        for ws in self._snapshot():
            try:
                await ws.send_text(text)
            except Exception:
                dead.append(ws)
        with self._lock:
            for ws in dead:
                try:
                    self._connections.remove(ws)
                except ValueError:
                    pass


_manager = _ConnectionManager()


def _on_frame(image, detections) -> None:
    if _loop is None:
        return
    annotated = annotate(image, detections)
    _, jpeg = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
    asyncio.run_coroutine_threadsafe(_manager.broadcast_bytes(jpeg.tobytes()), _loop)


def _on_alert(light) -> None:
    if _loop is None:
        return
    msg = json.dumps({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "bearing": round(light.bearing, 1),
        "color": light.color,
        "confidence": 1.0,
    })
    asyncio.run_coroutine_threadsafe(_manager.broadcast_text(msg), _loop)


def run_web(source, proxy, opencv_analyzer, yolo_analyzer, logger, tracker=None, min_confidence: float = 0.0, port: int = 8000) -> None:
    def pipeline_thread():
        from pipeline import run
        run(source, proxy, logger,
            on_frame=_on_frame,
            on_alert=_on_alert if tracker else None,
            tracker=tracker,
            min_confidence=min_confidence)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        global _loop
        _loop = asyncio.get_running_loop()
        threading.Thread(target=pipeline_thread, daemon=True).start()
        yield

    app = FastAPI(lifespan=lifespan)

    @app.get("/")
    def index() -> HTMLResponse:
        html = (Path(__file__).parent / "static" / "index.html").read_text()
        return HTMLResponse(html)

    @app.get("/api/status")
    def status() -> JSONResponse:
        from analysis.yolo_analyzer import YOLOAnalyzer
        return JSONResponse({
            "analyzer": "yolo" if "YOLO" in proxy.name() else "opencv",
            "yolo_available": YOLOAnalyzer.available,
        })

    @app.post("/api/analyzer")
    async def set_analyzer(request: Request) -> JSONResponse:
        body = await request.json()
        choice = body.get("type")
        if choice == "yolo":
            if yolo_analyzer is None:
                return JSONResponse({"error": "YOLO not available — run: pip install ultralytics"}, status_code=400)
            proxy.set(yolo_analyzer)
        elif choice == "opencv":
            proxy.set(opencv_analyzer)
        else:
            return JSONResponse({"error": "unknown type"}, status_code=400)
        return JSONResponse({"analyzer": choice})

    @app.websocket("/ws")
    async def ws_endpoint(ws: WebSocket) -> None:
        await _manager.connect(ws)
        try:
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            await _manager.disconnect(ws)

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
