from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MenuTile:
    key: str
    title: str
    subtitle: str
    detail: str
