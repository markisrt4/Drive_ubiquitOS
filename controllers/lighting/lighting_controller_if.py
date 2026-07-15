from __future__ import annotations

from concurrent.futures import Future
from typing import Protocol, runtime_checkable

from controllers.lighting.lighting_types import (
    CustomPatternMode,
    LightingState,
    RgbColor,
)


@runtime_checkable
class LightingControllerIf(Protocol):
    """Thread-friendly controller contract for lighting applications."""

    @property
    def is_connected(self) -> bool: ...

    def current_state(self) -> LightingState: ...

    def connect(self) -> Future[None]: ...

    def disconnect(self) -> Future[None]: ...

    def close(self) -> None: ...

    def set_power(self, enabled: bool) -> Future[None]: ...

    def set_color(self, color: RgbColor) -> Future[None]: ...

    def set_brightness(self, percent: int) -> Future[None]: ...

    def set_color_temperature(self, percent: int) -> Future[None]: ...

    def set_pattern(self, pattern_index: int) -> Future[None]: ...

    def set_music_mode(self, eq_mode: int) -> Future[None]: ...

    def set_custom_pattern_mode(
        self,
        mode: CustomPatternMode,
    ) -> Future[None]: ...

    def set_custom_pattern_direction(
        self,
        is_forward: bool,
    ) -> Future[None]: ...
