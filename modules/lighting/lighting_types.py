from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class RgbColor:
    red: int
    green: int
    blue: int

    def __post_init__(self) -> None:
        for name, value in (
            ("red", self.red),
            ("green", self.green),
            ("blue", self.blue),
        ):
            if not 0 <= value <= 255:
                raise ValueError(f"{name} must be in range 0..255")


@dataclass(frozen=True, slots=True)
class LightingState:
    power_enabled: bool
    color: RgbColor
    brightness_percent: int
    pattern_index: int
    music_mode: int

    def __post_init__(self) -> None:
        if not 0 <= self.brightness_percent <= 100:
            raise ValueError("brightness_percent must be in range 0..100")
        if not 0 <= self.pattern_index <= 210:
            raise ValueError("pattern_index must be in range 0..210")
        if not 0 <= self.music_mode <= 255:
            raise ValueError("music_mode must be in range 0..255")


class CustomPatternMode(Enum):
    GRADUAL = 0     # GD
    FADE = 1        # FD
    FORWARD = 2     # FW
    FLASH = 3       # FS
    OFF = 4         # AC
    PULSE = 5       # PU
    FLOW = 6        # FL
    HOP = 7         # HO
