import tkinter as tk
from dataclasses import dataclass
from typing import Callable

from apps.common.uiTheme import COLORS, MENU_TILE_STYLE


@dataclass(frozen=True, slots=True)
class MenuTile:
    key: str
    title: str
    subtitle: str
    detail: str


@dataclass(frozen=True, slots=True)
class MenuPage:
    title: str
    tiles: tuple[MenuTile, ...]
    columns: int = 3


class MenuRenderer:
    def __init__(
        self,
        content_frame: tk.Frame,
        compact_ui: bool,
        on_tile_clicked: Callable[[str], None],
    ) -> None:
        self._content_frame = content_frame
        self._compact_ui = compact_ui
        self._on_tile_clicked = on_tile_clicked

    def show_page(self, page: MenuPage) -> None:
        self._clear_content()

        style = self._style()

        dashboard = tk.Frame(self._content_frame, bg=COLORS["app_bg"])
        dashboard.pack(fill="both", expand=True)

        columns = max(1, page.columns)
        rows = max(1, (len(page.tiles) + columns - 1) // columns)

        for col in range(columns):
            dashboard.columnconfigure(col, weight=1, uniform="dash_col")

        for row in range(rows):
            dashboard.rowconfigure(row, weight=1, uniform="dash_row")

        for index, tile_spec in enumerate(page.tiles):
            row = index // columns
            col = index % columns

            tile = self.create_tile(
                parent=dashboard,
                tile=tile_spec,
                is_main_tile=True,
            )

            tile.grid(
                row=row,
                column=col,
                sticky="nsew",
                padx=style["tile_padx"],
                pady=style["tile_pady"],
            )

    def create_tile(
        self,
        parent: tk.Widget,
        tile: MenuTile,
        is_main_tile: bool = False,
    ) -> tk.Frame:
        style = self._style()
        is_preset = "_preset_" in tile.key and not is_main_tile

        title_font = self._title_font(
            style=style,
            is_main_tile=is_main_tile,
            is_preset=is_preset,
        )

        tile_frame = tk.Frame(
            parent,
            bg=COLORS["tile_bg"],
            highlightthickness=2,
            highlightbackground=COLORS["tile_border"],
            highlightcolor=COLORS["tile_accent"],
            bd=0,
            cursor="hand2",
        )

        accent = tk.Frame(
            tile_frame,
            bg=COLORS["tile_accent"],
            height=style["accent_height"],
        )
        accent.pack(fill="x", side="top")

        body = tk.Frame(tile_frame, bg=COLORS["tile_bg"])
        body.pack(
            fill="both",
            expand=True,
            padx=style["body_padx"],
            pady=style["body_pady"],
        )

        title_label = tk.Label(
            body,
            text=tile.title,
            font=title_font,
            bg=COLORS["tile_bg"],
            fg=COLORS["tile_title"],
            anchor="center" if is_preset else "w",
            justify="center" if is_preset else "left",
            wraplength=style["title_wrap"],
        )
        title_label.pack(fill="x", anchor="center" if is_preset else "w")

        subtitle_label = tk.Label(
            body,
            text=tile.subtitle,
            font=style["subtitle_font"],
            bg=COLORS["tile_bg"],
            fg=COLORS["tile_subtitle"],
            anchor="center" if is_preset else "w",
            justify="center" if is_preset else "left",
            wraplength=style["text_wrap"],
        )
        subtitle_label.pack(
            fill="x",
            anchor="center" if is_preset else "w",
            pady=(3, 0),
        )

        detail_label = tk.Label(
            body,
            text=tile.detail,
            font=style["detail_font"],
            bg=COLORS["tile_bg"],
            fg=COLORS["tile_detail"],
            anchor="center" if is_preset else "w",
            justify="center" if is_preset else "left",
            wraplength=style["text_wrap"],
        )
        detail_label.pack(
            fill="x",
            anchor="center" if is_preset else "w",
            pady=(2, 0),
        )

        self._bind_click_recursive(tile_frame, tile.key)
        return tile_frame

    def _style(self) -> dict[str, object]:
        return MENU_TILE_STYLE["compact" if self._compact_ui else "normal"]

    @staticmethod
    def _title_font(
        style: dict[str, object],
        is_main_tile: bool,
        is_preset: bool,
    ) -> tuple[str, int] | tuple[str, int, str]:
        if is_main_tile:
            return style["main_title_font"]

        if is_preset:
            return style["preset_title_font"]

        return style["default_title_font"]

    def _bind_click_recursive(self, widget: tk.Widget, key: str) -> None:
        widget.bind("<Button-1>", lambda event, k=key: self._on_tile_clicked(k))

        if isinstance(widget, (tk.Frame, tk.Label)):
            for child in widget.winfo_children():
                self._bind_click_recursive(child, key)

    def _clear_content(self) -> None:
        for child in self._content_frame.winfo_children():
            child.destroy()
