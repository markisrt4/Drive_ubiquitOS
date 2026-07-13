from abc import ABC, abstractmethod

from controllers.spotify.spotify_state import SpotifyState


class SpotifyControllerIf(ABC):
    @abstractmethod
    def current_state(self) -> SpotifyState:
        pass

    @abstractmethod
    def play_pause(self) -> None:
        pass

    @abstractmethod
    def next_track(self) -> None:
        pass

    @abstractmethod
    def previous_track(self) -> None:
        pass

    @abstractmethod
    def set_volume_percent(self, volume_percent: int) -> None:
        pass

    @abstractmethod
    def seek_to_position_ms(self, position_ms: int) -> None:
        pass
