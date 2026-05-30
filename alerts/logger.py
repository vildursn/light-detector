import sqlite3
from datetime import datetime

from analysis.base import Detection


class Logger:
    def __init__(self, db_path: str = "detections.db"):
        self._conn = sqlite3.connect(db_path)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS detections (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                bearing   REAL,
                color     TEXT,
                confidence REAL
            )
        """)
        self._conn.commit()

    def log(self, detection: Detection) -> None:
        ts = datetime.now().isoformat(timespec="seconds")
        self._conn.execute(
            "INSERT INTO detections (timestamp, bearing, color, confidence) VALUES (?, ?, ?, ?)",
            (ts, detection.bearing, detection.color, detection.confidence),
        )
        self._conn.commit()
        print(f"[{ts}] bearing={detection.bearing:+.1f}°  color={detection.color}  conf={detection.confidence:.2f}")

    def close(self) -> None:
        self._conn.close()
