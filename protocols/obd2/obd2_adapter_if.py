from __future__ import annotations

from abc import ABC, abstractmethod

from protocols.obd2.obd2_request import Obd2Request
from protocols.obd2.obd2_response import Obd2Response


class Obd2AdapterIf(ABC):
    """Transport-independent interface for SAE J1979 requests.

    A functional request may be answered by more than one ECU. Therefore
    ``request`` returns every normalized response. No response is represented
    by an empty tuple rather than ``None``.
    """

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        ...

    @abstractmethod
    def connect(self) -> None:
        ...

    @abstractmethod
    def disconnect(self) -> None:
        ...

    @abstractmethod
    def request(self, request: Obd2Request) -> tuple[Obd2Response, ...]:
        ...
