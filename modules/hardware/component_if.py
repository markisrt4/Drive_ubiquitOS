from abc import ABC, abstractmethod
from typing import Any

from dataclasses import dataclass


@dataclass(frozen=True)
class ComponentStatus:
    name: str
    running: bool
    available: bool
    last_error: str | None = None


class ComponentIf(ABC):
    def __init__(self, name: str):
        self.name = name
        self.running = False
        self.available = False
        self.last_error: str | None = None

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def status(self) -> ComponentStatus:
        pass

    def is_running(self) -> bool:
        return self.running

    def is_available(self) -> bool:
        return self.available
