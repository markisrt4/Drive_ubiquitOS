from abc import ABC, abstractmethod

from hardware_io.buttons.push_button_types import PushButtonState


class PushButtonIf(ABC):
    @abstractmethod
    def start(self) -> None:
        """Begin monitoring the button."""

    @abstractmethod
    def stop(self) -> None:
        """Stop monitoring the button."""

    @abstractmethod
    def get_state(self) -> PushButtonState:
        """Return the current button state."""