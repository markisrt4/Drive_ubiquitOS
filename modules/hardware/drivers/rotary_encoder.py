from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Callable, Optional

import RPi.GPIO as GPIO


RotateCallback = Callable[[int], None]
ButtonCallback = Callable[[], None]


@dataclass(frozen=True)
class RotaryEncoderPins:
    pin_a: int
    pin_b: int
    button: int


class RotaryEncoder:
    """
    Interrupt-driven rotary encoder using BCM GPIO numbering.

    Call tick() periodically from your main loop to dispatch accumulated
    rotary movement safely.
    """

    def __init__(
        self,
        pins: RotaryEncoderPins,
        rotate_callback: Optional[RotateCallback] = None,
        button_callback: Optional[ButtonCallback] = None,
        button_bounce_ms: int = 200,
    ) -> None:
        self.pins = pins
        self.rotate_callback = rotate_callback
        self.button_callback = button_callback
        self.button_bounce_ms = button_bounce_ms

        self._rotary_counter = 0
        self._current_a = 1
        self._current_b = 1
        self._lock = Lock()
        self._started = False

    def start(self) -> None:
        if self._started:
            return

        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.pins.pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pins.pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pins.button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(
            self.pins.pin_a,
            GPIO.RISING,
            callback=self._rotary_interrupt,
        )

        GPIO.add_event_detect(
            self.pins.pin_b,
            GPIO.RISING,
            callback=self._rotary_interrupt,
        )

        if self.button_callback is not None:
            GPIO.add_event_detect(
                self.pins.button,
                GPIO.FALLING,
                callback=self._button_interrupt,
                bouncetime=self.button_bounce_ms,
            )

        self._started = True

    def stop(self) -> None:
        if not self._started:
            return

        GPIO.remove_event_detect(self.pins.pin_a)
        GPIO.remove_event_detect(self.pins.pin_b)
        GPIO.remove_event_detect(self.pins.button)

        self._started = False

    def cleanup(self) -> None:
        self.stop()
        GPIO.cleanup()

    def set_rotate_callback(self, callback: RotateCallback) -> None:
        self.rotate_callback = callback

    def set_button_callback(self, callback: ButtonCallback) -> None:
        self.button_callback = callback

    def tick(self) -> None:
        """
        Dispatch accumulated rotation.

        Safe to call from:
        - a while loop
        - a Tkinter root.after() loop
        - another application-level scheduler
        """

        with self._lock:
            delta = self._rotary_counter
            self._rotary_counter = 0

        if delta != 0 and self.rotate_callback is not None:
            self.rotate_callback(delta)

    def _rotary_interrupt(self, channel: int) -> None:
        switch_a = GPIO.input(self.pins.pin_a)
        switch_b = GPIO.input(self.pins.pin_b)

        if self._current_a == switch_a and self._current_b == switch_b:
            return

        self._current_a = switch_a
        self._current_b = switch_b

        if switch_a and switch_b:
            with self._lock:
                if channel == self.pins.pin_a:
                    self._rotary_counter += 1
                else:
                    self._rotary_counter -= 1

    def _button_interrupt(self, channel: int) -> None:
        if self.button_callback is not None:
            self.button_callback()

    def __enter__(self) -> RotaryEncoder:
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.cleanup()
