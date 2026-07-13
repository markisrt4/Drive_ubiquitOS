from __future__ import annotations

from abc import ABC, abstractmethod


class AudioBackendIf(ABC):
    """
    Interface for controlling an audio output backend.
    """

    @abstractmethod
    def volume_up(self) -> int:
        """
        Increase volume and return the resulting level.
        """

    @abstractmethod
    def volume_down(self) -> int:
        """
        Decrease volume and return the resulting level.
        """

    @abstractmethod
    def get_volume_level(self) -> int:
        """
        Return the current discrete volume level.
        """

    @abstractmethod
    def set_volume_level(self, level: int) -> int:
        """
        Set and return the resulting discrete volume level.
        """
