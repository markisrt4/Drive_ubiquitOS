from __future__ import annotations

from typing import Callable

from input_device_if import InputDeviceIf
from modules.hardware.drivers.rotary_encoder import RotaryEncoder, RotaryEncoderPins


class RotaryEncoderDevice(InputDeviceIf):
    """
    InputDevice wrapper around RotaryEncoder.

    Converts low-level encoder movement into named input events:

        rotate_left
        rotate_right
        press

    This lets the main application bind actions without caring about GPIO.
    """

    ROTATE_LEFT = "rotate_left"
    ROTATE_RIGHT = "rotate_right"
    PRESS = "press"

    def __init__(
        self,
        pins: RotaryEncoderPins,
        name: str = "rotary_encoder",
        button_bounce_ms: int = 200,
    ) -> None:
        self.name = name
        self.bindings: dict[str, Callable[[], None]] = {}
        self.enabled = False

        self.encoder = RotaryEncoder(
            pins=pins,
            rotate_callback=self._on_rotate,
            button_callback=self._on_press,
            button_bounce_ms=button_bounce_ms,
        )

    def bind(self, input_name: str, callback: Callable[[], None]) -> None:
        self.bindings[input_name] = callback

    def unbind(self, input_name: str) -> None:
        self.bindings.pop(input_name, None)

    def start(self) -> None:
        if self.enabled:
            return

        self.encoder.start()
        self.enabled = True

    def stop(self) -> None:
        if not self.enabled:
            return

        self.encoder.stop()
        self.enabled = False

    def tick(self) -> None:
        """
        Dispatch accumulated encoder movement.

        Call this from the a main loop or another scheduler.
        """
        if self.enabled:
            self.encoder.tick()

    def cleanup(self) -> None:
        self.encoder.cleanup()
        self.enabled = False

    def _on_rotate(self, delta: int) -> None:
        if delta > 0:
            self._dispatch(self.ROTATE_RIGHT)
        elif delta < 0:
            self._dispatch(self.ROTATE_LEFT)

    def _on_press(self) -> None:
        self._dispatch(self.PRESS)

    def _dispatch(self, input_name: str) -> None:
        callback = self.bindings.get(input_name)

        if callback is not None:
            callback()
