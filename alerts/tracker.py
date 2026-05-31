import time
from dataclasses import dataclass
from typing import List, Optional

from analysis.base import Detection


@dataclass
class TrackedLight:
    color: str
    bearing: float
    first_seen: float
    last_seen: float
    alert_sent: bool = False
    last_alert: float = 0.0


class LightTracker:
    def __init__(self, config):
        self._config = config
        self._lights: List[TrackedLight] = []

    def update(self, detections: List[Detection]) -> List[TrackedLight]:
        """Update tracker with detections from one frame. Returns newly confirmed lights."""
        now = time.time()

        for det in detections:
            match = self._find_match(det)
            if match is not None:
                match.last_seen = now
                match.bearing = det.bearing
            else:
                self._lights.append(TrackedLight(
                    color=det.color,
                    bearing=det.bearing,
                    first_seen=now,
                    last_seen=now,
                ))

        self._lights = [
            l for l in self._lights
            if now - l.last_seen < self._config.light_gone_after_seconds
        ]

        confirmed = []
        for light in self._lights:
            age = now - light.first_seen
            if not light.alert_sent and age >= self._config.confirm_after_seconds:
                light.alert_sent = True
                light.last_alert = now
                confirmed.append(light)
            elif light.alert_sent and now - light.last_alert >= self._config.alert_cooldown_seconds:
                light.last_alert = now
                confirmed.append(light)

        return confirmed

    def _find_match(self, detection: Detection) -> Optional[TrackedLight]:
        tol = self._config.track_bearing_tolerance
        for light in self._lights:
            if light.color == detection.color and abs(light.bearing - detection.bearing) <= tol:
                return light
        return None
