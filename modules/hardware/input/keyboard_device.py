import tkinter as tk
from typing import Callable

from modules.hardware.component_if import ComponentIf, ComponentStatus
from modules.hardware.input.input_device_if import InputDeviceIf


class KeyboardDevice(ComponentIf, InputDeviceIf):
    """
    Keyboard input device.

    Provides a simple mapping between Tkinter key bindings
    and application callbacks.

    Example:

        keyboard.bind("<Left>", tune_down)
        keyboard.bind("<Right>", tune_up)
        keyboard.bind("<Return>", select)

        keyboard.start()
    """

    def __init__(self, root: tk.Widget, name: str = "keyboard"):
        ComponentIf.__init__(self, name)

        self._root = root
        self._bindings: dict[str, Callable[[], None]] = {}

        self.available = True

    #
    # InputDeviceIf
    #

    def bind(
        self,
        input_name: str,
        callback: Callable[[], None],
    ) -> None:
        self._bindings[input_name] = callback

        if self.running:
            self._bind_key(input_name, callback)

    def unbind(self, input_name: str) -> None:
        self._bindings.pop(input_name, None)

        if self.running:
            self._root.unbind_all(input_name)

    #
    # ComponentIf
    #

    def start(self) -> None:
        if self.running:
            return

        for input_name, callback in self._bindings.items():
            self._bind_key(input_name, callback)

        self.running = True

    def stop(self) -> None:
        if not self.running:
            return

        for input_name in self._bindings:
            self._root.unbind_all(input_name)

        self.running = False

    def status(self) -> ComponentStatus:
        return ComponentStatus(
            name=self.name,
            running=self.running,
            available=self.available,
            last_error=self.last_error,
    )

    #
    # Private
    #

    def _bind_key(
        self,
        input_name: str,
        callback: Callable[[], None],
    ) -> None:
        self._root.bind_all(
            input_name,
            lambda event: callback(),
        )
