from __future__ import annotations

from concurrent.futures import Future

from .lighting_controller_if import LightingControllerIf
from .lighting_types import CustomPatternMode, RgbColor


class DummyLightingController(LightingControllerIf):
    """No-hardware controller for UI development and screenshots."""

    def __init__(self) -> None:
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> Future[None]:
        self._connected = True
        return self._done()

    def disconnect(self) -> Future[None]:
        self._connected = False
        return self._done()

    def close(self) -> None:
        self._connected = False

    def set_power(self, enabled: bool) -> Future[None]:
        print(f"[DummyLighting] power={enabled}")
        return self._done()

    def set_color(self, color: RgbColor) -> Future[None]:
        print(f"[DummyLighting] color={color}")
        return self._done()

    def set_brightness(self, percent: int) -> Future[None]:
        print(f"[DummyLighting] brightness={percent}")
        return self._done()

    def set_color_temperature(self, percent: int) -> Future[None]:
        print(f"[DummyLighting] color_temperature={percent}")
        return self._done()

    def set_pattern(self, pattern_index: int) -> Future[None]:
        print(f"[DummyLighting] pattern={pattern_index}")
        return self._done()

    def set_music_mode(self, eq_mode: int) -> Future[None]:
        print(f"[DummyLighting] music_mode={eq_mode}")
        return self._done()

    def set_custom_pattern_mode(self, mode: CustomPatternMode) -> Future[None]:
        print(f"[DummyLighting] custom_pattern_mode={mode.name}")
        return self._done()

    def set_custom_pattern_direction(self, is_forward: bool) -> Future[None]:
        print(f"[DummyLighting] custom_pattern_direction={is_forward}")
        return self._done()

    @staticmethod
    def _done() -> Future[None]:
        future: Future[None] = Future()
        future.set_result(None)
        return future
