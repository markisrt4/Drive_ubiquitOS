from typing import Protocol, TypeVar


T = TypeVar("T")


class ObdPid(Protocol[T]):
    @property
    def pid(self) -> str:
        ...

    def decode(self, response: str) -> T | None:
        ...


def byte_at(response: str, index: int) -> int:
    return int(response[index:index + 2], 16)
