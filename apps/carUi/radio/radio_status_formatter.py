from __future__ import annotations

from modules.radio.radio_types import RadioPreset


def format_frequency(frequency_hz: int) -> str:
    if frequency_hz >= 1_000_000:
        value = f"{frequency_hz / 1_000_000:.3f}".rstrip("0").rstrip(".")
        return f"{value} MHz"

    if frequency_hz >= 1_000:
        value = f"{frequency_hz / 1_000:.3f}".rstrip("0").rstrip(".")
        return f"{value} kHz"

    return f"{frequency_hz} Hz"


def compact_preset_label(preset: RadioPreset) -> str:
    if preset.frequency_hz >= 1_000_000:
        value = preset.frequency_hz / 1_000_000
        return f"{value:.1f}".rstrip("0").rstrip(".")

    return preset.label


def format_step(step_hz: int) -> str:
    if step_hz >= 1_000_000:
        return f"{step_hz / 1_000_000:g} MHz"

    if step_hz >= 1_000:
        return f"{step_hz / 1_000:g} kHz"

    return f"{step_hz:g} Hz"
