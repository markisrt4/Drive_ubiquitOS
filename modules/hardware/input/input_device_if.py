from abc import ABC, abstractmethod
from typing import Callable


class InputDeviceIf(ABC):
    @abstractmethod
    def bind(self, input_name: str, callback: Callable[[], None]) -> None:
        pass

    @abstractmethod
    def unbind(self, input_name: str) -> None:
        pass
