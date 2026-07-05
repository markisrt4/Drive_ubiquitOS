from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from modules.lighting.lighting_types import CustomPatternMode, RgbColor


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(value, upper))


class LedDmxProtocol:
    """Packet builders for LEDDMX-00 / LEDDMX-03 BLE controllers.

    BLE service: 0000FFE0-0000-1000-8000-00805F9B34FB
    BLE write characteristic: 0000FFE1-0000-1000-8000-00805F9B34FB
    """

    @staticmethod
    def power(enabled: bool) -> bytes:
        return bytes([0x7B, 0xFF, 0x04, 0x03 if enabled else 0x02, 0xFF, 0xFF, 0xFF, 0xFF, 0xBF])

    @staticmethod
    def color(color: RgbColor) -> bytes:
        return bytes([0x7B, 0xFF, 0x07, color.red, color.green, color.blue, 0x00, 0xFF, 0xBF])

    @staticmethod
    def brightness(percent: int) -> bytes:
        brightness_percent = _clamp(percent, 0, 100)
        adjusted_percent = (brightness_percent * 32) // 100
        return bytes([0x7B, 0xFF, 0x01, adjusted_percent, brightness_percent, 0x00, 0xFF, 0xFF, 0xBF])

    @staticmethod
    def color_temperature(percent: int) -> bytes:
        temperature_percent = _clamp(percent, 0, 100)
        adjusted_percent = (temperature_percent * 32) // 100
        return bytes([0x7B, 0xFF, 0x09, adjusted_percent, temperature_percent, 0xFF, 0xFF, 0xFF, 0xBF])

    @staticmethod
    def pattern(index: int) -> bytes:
        pattern_index = _clamp(index, 0, 210)
        return bytes([0x7B, 0xFF, 0x03, pattern_index, 0xFF, 0xFF, 0xFF, 0xFF, 0xBF])

    @staticmethod
    def mic_eq(eq_mode: int) -> bytes:
        mode = _clamp(eq_mode, 0, 255)
        return bytes([0x7B, 0xFF, 0x0B, mode, 0x00, 0xFF, 0xFF, 0xBF])

    @staticmethod
    def custom_pattern_color(color: RgbColor, list_position: int, list_size: int) -> bytes:
        position = _clamp(list_position, 1, 255)
        size = _clamp(list_size, 1, 255)
        return bytes([0x7B, position, 0x0E, 0xFD, color.red, color.green, color.blue, size, 0xBF])

    @staticmethod
    def custom_pattern_mode(mode: CustomPatternMode) -> bytes:
        return bytes([0x7B, 0xFF, 0x13, mode.value, 0xFF, 0xFF, 0xFF, 0xFF, 0xBF])

    @staticmethod
    def custom_pattern_direction(is_forward: bool) -> bytes:
        return bytes([0x7B, 0xFF, 0x0D, 0x00 if is_forward else 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xBF])

    @staticmethod
    def timing(
        *,
        hour: int,
        minute: int,
        mode: int,
        weekdays: Sequence[bool],
        list_position: int,
        now: datetime | None = None,
    ) -> bytes:
        current = now or datetime.now()
        current_day = current.isoweekday()  # Monday=1, Sunday=7
        packed_day_and_position = (current_day << 4) | _clamp(list_position, 0, 15)
        packed_weekdays = 0
        if len(weekdays) != 7:
            raise ValueError("weekdays must contain seven bool values, Monday first")
        for index, enabled in enumerate(weekdays):
            if enabled:
                packed_weekdays |= 1 << index
        return bytes([
            0x8B,
            packed_day_and_position,
            _clamp(mode, 0, 255),
            packed_weekdays,
            _clamp(hour, 0, 24),
            _clamp(minute, 0, 59),
            current.hour,
            current.minute,
            0xBF,
        ])

    @staticmethod
    def timing_termination(list_size: int, now: datetime | None = None) -> bytes:
        current = now or datetime.now()
        current_day = current.isoweekday()
        return bytes([0x7B, 0xFF, 0x10, current_day, _clamp(list_size, 0, 255), 0xFF, current.hour, current.minute, 0xBF])
