from __future__ import annotations

from concurrent.futures import Future
from typing import Protocol

from .lighting_types import CustomPatternMode, RgbColor


class LightingControllerIf(Protocol):
    """Thread-friendly lighting controller interface for UI code.

    Tkinter panels should not await coroutines or call asyncio.run(). Concrete
    controllers may use asyncio internally, but UI code receives a Future and
    can attach a completion callback without blocking the main loop.
    """

    @property
    def is_connected(self) -> bool: ...

    def connect(self) -> Future[None]: ...

    def disconnect(self) -> Future[None]: ...

    def close(self) -> None: ...

    def set_power(self, enabled: bool) -> Future[None]: ...

    def set_color(self, color: RgbColor) -> Future[None]: ...

    def set_brightness(self, percent: int) -> Future[None]: ...

    def set_color_temperature(self, percent: int) -> Future[None]: ...

    def set_pattern(self, pattern_index: int) -> Future[None]: ...

    def set_music_mode(self, eq_mode: int) -> Future[None]: ...

    def set_custom_pattern_mode(self, mode: CustomPatternMode) -> Future[None]: ...

    def set_custom_pattern_direction(self, is_forward: bool) -> Future[None]: ...
