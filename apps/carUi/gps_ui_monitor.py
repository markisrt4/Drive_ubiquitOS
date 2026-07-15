from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from hardware_io.gps.gps_reader import GpsData, GpsReader


class GPSUIMonitor:
    """Bridge callback-driven GPS data into Tk-safe UI updates."""

    def __init__(
        self,
        *,
        root: tk.Misc,
        gps_reader: GpsReader,
        set_position: Callable[[float | None, float | None], None],
        set_status: Callable[[str], None] | None = None,
    ) -> None:
        self._root = root
        self._gps_reader = gps_reader
        self._set_position = set_position
        self._set_status = set_status
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running and self._gps_reader.is_running

    def start(self) -> None:
        if self._running:
            return

        self._running = True
        self._publish_status("GPS starting")
        self._gps_reader.start(callback=self._on_gps_data)

    def stop(self) -> None:
        if not self._running:
            return

        self._running = False
        self._gps_reader.stop()

    def close(self) -> None:
        self._running = False
        self._gps_reader.close()

    def _on_gps_data(self, data: GpsData) -> None:
        if not self._running:
            return

        self._root.after(
            0,
            lambda current=data: self._apply_gps_data(current),
        )

    def _apply_gps_data(self, data: GpsData) -> None:
        if not self._running:
            return

        if (
            data.has_fix
            and data.latitude is not None
            and data.longitude is not None
        ):
            self._set_position(data.latitude, data.longitude)
            self._publish_status(self._format_fix_status(data))
            return

        self._set_position(None, None)
        self._publish_status("GPS searching")

    def _format_fix_status(self, data: GpsData) -> str:
        if data.satellites_used is None:
            return "GPS fix acquired"

        visible = (
            data.satellites_visible
            if data.satellites_visible is not None
            else "?"
        )
        return (
            f"GPS fix acquired: "
            f"{data.satellites_used}/{visible} satellites"
        )

    def _publish_status(self, message: str) -> None:
        if self._set_status is not None:
            self._set_status(message)
