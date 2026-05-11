from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RadioStatusSnapshot:
    frequency_hz: Optional[int] = None
    mode: Optional[str] = None
    preset_label: Optional[str] = None
    preset_index: Optional[int] = None
    preset_count: Optional[int] = None
    signal_strength: Optional[str] = None
    snr: Optional[str] = None
    rds: Optional[str] = None


@dataclass(frozen=True)
class RadioPanelTileConfig:
    label: str
    subtitle: str
    detail: str


@dataclass(frozen=True)
class RadioPanelConfig:
    key: str
    title: str
    launch_tile: RadioPanelTileConfig
    radio_toggle_tile: RadioPanelTileConfig
    default_step_hz: int
    default_mode_name: str = "Radio"
    preset_columns: int = 2
