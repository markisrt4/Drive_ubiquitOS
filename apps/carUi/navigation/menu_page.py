from dataclasses import dataclass
from apps.carUi.navigation.menu_tile import MenuTile


@dataclass(frozen=True, slots=True)
class MenuPage:
    title: str
    tiles: tuple[MenuTile, ...]
    columns: int = 3
