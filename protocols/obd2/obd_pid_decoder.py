from __future__ import annotations

from typing import Protocol, TypeVar


T_co = TypeVar("T_co", covariant=True)


class ObdPidDecoder(Protocol[T_co]):
    """Decoder contract for a standardized OBD-II PID.

    Decoders return values in the canonical units defined by SAE J1979.
    Display-unit conversion belongs in the application or presentation layer.
    """

    @property
    def mode(self) -> int:
        ...

    @property
    def pid(self) -> int:
        ...

    @property
    def unit(self) -> str:
        ...

    def decode(self, data: bytes) -> T_co | None:
        ...


def byte_at(data: bytes, index: int) -> int:
    try:
        return data[index]
    except IndexError:
        raise ValueError(f"OBD-II response does not contain byte {index}") from None
