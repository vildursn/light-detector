import asyncio
import json
import threading
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import cv2
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

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
    frame_bytes = jpeg.tobytes()
    asyncio.run_coroutine_threadsafe(_manager.broadcast_bytes(frame_bytes), _loop)
    for d in detections:
        msg = json.dumps({
            "ts": datetime.now().isoformat(timespec="seconds"),
            "bearing": round(d.bearing, 1),
            "color": d.color,
            "confidence": round(d.confidence, 2),
        })
        asyncio.run_coroutine_threadsafe(_manager.broadcast_text(msg), _loop)


def run_web(source, analyzer, logger, port: int = 8000) -> None:
    def pipeline_thread():
        from pipeline import run
        run(source, analyzer, logger, on_frame=_on_frame)

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

    @app.websocket("/ws")
    async def ws_endpoint(ws: WebSocket) -> None:
        await _manager.connect(ws)
        try:
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            await _manager.disconnect(ws)

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
