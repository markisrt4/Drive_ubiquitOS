from __future__ import annotations

from dataclasses import dataclass

from modules.hardware.input.rotary_encoder_device import RotaryEncoderDevice
from modules.sdr.rigctl_client import RigctlClient


@dataclass(frozen=True)
class RotaryRigctlAdapterConfig:
    step_hz: int = 25_000


class RotaryRigctlAdapter:
    """
    Adapts RotaryEncoderDevice input events into rigctl frequency commands.

    It maps logical encoder input to radio control behavior.
    """

    def __init__(
        self,
        encoder: RotaryEncoderDevice,
        rigctl: RigctlClient,
        config: RotaryRigctlAdapterConfig | None = None,
    ) -> None:
        self._encoder = encoder
        self._rigctl = rigctl
        self._config = config or RotaryRigctlAdapterConfig()

    def bind(self) -> None:
        self._encoder.bind(
            RotaryEncoderDevice.ROTATE_LEFT,
            self._tune_down,
        )

        self._encoder.bind(
            RotaryEncoderDevice.ROTATE_RIGHT,
            self._tune_up,
        )

        self._encoder.bind(
            RotaryEncoderDevice.PRESS,
            self._on_press,
        )

    def _tune_up(self) -> None:
        self._adjust_frequency(self._config.step_hz)

    def _tune_down(self) -> None:
        self._adjust_frequency(-self._config.step_hz)

    def _on_press(self) -> None:
        # Placeholder behavior.
        # Later this could toggle mute, change step size, switch band, etc.
        print("Rotary encoder button pressed")

    def _adjust_frequency(self, delta_hz: int) -> None:
        current_freq_hz = self._rigctl.get_frequency()
        next_freq_hz = current_freq_hz + delta_hz

        self._rigctl.set_frequency(next_freq_hz)
