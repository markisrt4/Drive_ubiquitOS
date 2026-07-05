from __future__ import annotations

import tkinter as tk
from concurrent.futures import Future
from tkinter import ttk
from collections.abc import Callable
from typing import Final

from modules.lighting.lighting_controller_if import LightingControllerIf
from modules.lighting.lighting_types import RgbColor


class LightingPanel(tk.Frame):
    """CarSDR lighting panel.

    This panel deliberately does not know about BLE, LEDDMX packets, asyncio, or
    BlueZ's little collection of moods. It calls a thread-friendly lighting
    controller and receives Future completion callbacks.
    """

    _BACKGROUND: Final[str] = "#07111f"
    _CARD_BACKGROUND: Final[str] = "#0d1b2e"
    _CARD_BORDER: Final[str] = "#17456d"
    _TEXT: Final[str] = "#e8f2ff"
    _MUTED_TEXT: Final[str] = "#8fa8c4"
    _ACCENT: Final[str] = "#1e88e5"
    _ACCENT_DARK: Final[str] = "#12385a"
    _ERROR: Final[str] = "#ff6b6b"
    _OK: Final[str] = "#4ade80"

    _COLORS: Final[tuple[tuple[str, str, RgbColor], ...]] = (
        ("Red", "#ff2b2b", RgbColor(255, 0, 0)),
        ("Green", "#00d26a", RgbColor(0, 255, 0)),
        ("Blue", "#2684ff", RgbColor(0, 0, 255)),
        ("White", "#f8fafc", RgbColor(255, 255, 255)),
        ("Amber", "#ffb020", RgbColor(255, 120, 0)),
        ("Purple", "#b455ff", RgbColor(160, 0, 255)),
    )

    _PATTERNS: Final[tuple[tuple[str, int], ...]] = (
        ("Off", 0),
        ("Dreaming", 1),
        ("7 Color Flow", 3),
        ("Trail 7 Color", 23),
        ("Stream 7 Color", 39),
        ("Curtain 7 Color", 57),
        ("Hop 7 Color", 75),
        ("Strobe 7 Color", 78),
        ("Gradual 7 Color", 81),
    )

    _MUSIC_MODES: Final[tuple[tuple[str, int], ...]] = (
        ("Off", 0),
        ("Music EQ 1", 1),
        ("Music EQ 2", 2),
        ("Music EQ 3", 3),
        ("Music EQ 4", 4),
    )

    def __init__(
        self,
        parent: tk.Misc,
        lighting_controller: LightingControllerIf,
    ) -> None:
        super().__init__(parent, bg=self._BACKGROUND)

        self._lighting = lighting_controller
        self._brightness = tk.IntVar(value=75)
        self._brightness_text = tk.StringVar(value="75%")
        self._status = tk.StringVar(value="Connecting...")
        self._status_color = self._MUTED_TEXT
        self._pattern_name = tk.StringVar(value=self._PATTERNS[0][0])
        self._music_name = tk.StringVar(value=self._MUSIC_MODES[0][0])
        self._brightness_after_id: str | None = None

        self._status_label: tk.Label | None = None
        self._build_ui()
        self._submit(self._lighting.connect(), success_message="Connected")

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = tk.Frame(self, bg=self._BACKGROUND)
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(10, 4))
        header.columnconfigure(0, weight=1)

        tk.Label(
            header,
            text="Lighting",
            bg=self._BACKGROUND,
            fg=self._TEXT,
            font=("Arial", 24, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self._status_label = tk.Label(
            header,
            textvariable=self._status,
            bg=self._BACKGROUND,
            fg=self._status_color,
            font=("Arial", 12, "bold"),
        )
        self._status_label.grid(row=0, column=1, sticky="e")

        power = self._section(self, "Power")
        power.grid(row=1, column=0, sticky="ew", padx=18, pady=6)
        power.columnconfigure(0, weight=1)
        power.columnconfigure(1, weight=1)

        self._button(
            power,
            "ON",
            lambda: self._submit(self._lighting.set_power(True), success_message="Power on"),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=8, ipady=9)

        self._button(
            power,
            "OFF",
            lambda: self._submit(self._lighting.set_power(False), success_message="Power off"),
        ).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=8, ipady=9)

        body = tk.Frame(self, bg=self._BACKGROUND)
        body.grid(row=2, column=0, sticky="nsew", padx=18, pady=(2, 10))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=self._BACKGROUND)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.columnconfigure(0, weight=1)

        right = tk.Frame(body, bg=self._BACKGROUND)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right.columnconfigure(0, weight=1)

        self._build_brightness(left).grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self._build_colors(left).grid(row=1, column=0, sticky="nsew")
        self._build_modes(right).grid(row=0, column=0, sticky="nsew")

    def _build_brightness(self, parent: tk.Misc) -> tk.Frame:
        frame = self._section(parent, "Brightness")
        frame.columnconfigure(0, weight=1)

        tk.Label(
            frame,
            textvariable=self._brightness_text,
            bg=self._CARD_BACKGROUND,
            fg=self._ACCENT,
            font=("Arial", 16, "bold"),
        ).grid(row=0, column=1, sticky="e", padx=(8, 0))

        scale = tk.Scale(
            frame,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self._brightness,
            command=self._on_brightness_changed,
            bg=self._CARD_BACKGROUND,
            fg=self._TEXT,
            troughcolor=self._ACCENT_DARK,
            activebackground=self._ACCENT,
            highlightthickness=0,
            bd=0,
            length=320,
            showvalue=False,
        )
        scale.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 4))
        return frame

    def _build_colors(self, parent: tk.Misc) -> tk.Frame:
        frame = self._section(parent, "Colors")
        for column in range(3):
            frame.columnconfigure(column, weight=1)

        for index, (name, color_hex, rgb) in enumerate(self._COLORS):
            row = (index // 3) + 1
            column = index % 3
            fg = "#0b1220" if name == "White" else self._TEXT
            tk.Button(
                frame,
                text=name,
                bg=color_hex,
                fg=fg,
                activebackground=color_hex,
                activeforeground=fg,
                relief="flat",
                bd=0,
                font=("Arial", 12, "bold"),
                command=lambda c=rgb, n=name: self._submit(
                    self._lighting.set_color(c),
                    success_message=f"Color: {n}",
                ),
            ).grid(row=row, column=column, sticky="ew", padx=6, pady=7, ipady=13)

        return frame

    def _build_modes(self, parent: tk.Misc) -> tk.Frame:
        frame = self._section(parent, "Modes")
        frame.columnconfigure(0, weight=1)

        tk.Label(
            frame,
            text="Effect",
            bg=self._CARD_BACKGROUND,
            fg=self._MUTED_TEXT,
            font=("Arial", 12, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=(6, 4))

        pattern = ttk.Combobox(
            frame,
            textvariable=self._pattern_name,
            values=[name for name, _ in self._PATTERNS],
            state="readonly",
            font=("Arial", 13),
        )
        pattern.grid(row=2, column=0, sticky="ew", ipady=5)
        pattern.bind("<<ComboboxSelected>>", lambda _event: self._on_pattern_selected())

        tk.Label(
            frame,
            text="Music",
            bg=self._CARD_BACKGROUND,
            fg=self._MUTED_TEXT,
            font=("Arial", 12, "bold"),
        ).grid(row=3, column=0, sticky="w", pady=(20, 4))

        music = ttk.Combobox(
            frame,
            textvariable=self._music_name,
            values=[name for name, _ in self._MUSIC_MODES],
            state="readonly",
            font=("Arial", 13),
        )
        music.grid(row=4, column=0, sticky="ew", ipady=5)
        music.bind("<<ComboboxSelected>>", lambda _event: self._on_music_selected())

        quick = tk.Frame(frame, bg=self._CARD_BACKGROUND)
        quick.grid(row=5, column=0, sticky="ew", pady=(22, 0))
        quick.columnconfigure(0, weight=1)
        quick.columnconfigure(1, weight=1)

        self._button(
            quick,
            "Rainbow",
            lambda: self._set_pattern_by_name("7 Color Flow"),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6), ipady=8)

        self._button(
            quick,
            "Strobe",
            lambda: self._set_pattern_by_name("Strobe 7 Color"),
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0), ipady=8)

        return frame

    def _section(self, parent: tk.Misc, title: str) -> tk.Frame:
        frame = tk.Frame(
            parent,
            bg=self._CARD_BACKGROUND,
            padx=14,
            pady=10,
            highlightbackground=self._CARD_BORDER,
            highlightcolor=self._CARD_BORDER,
            highlightthickness=1,
            bd=0,
        )
        tk.Label(
            frame,
            text=title,
            bg=self._CARD_BACKGROUND,
            fg=self._TEXT,
            font=("Arial", 15, "bold"),
        ).grid(row=0, column=0, sticky="w", columnspan=3)
        return frame

    def _button(self, parent: tk.Misc, text: str, command: Callable[[], None]) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=self._ACCENT_DARK,
            fg=self._TEXT,
            activebackground=self._ACCENT,
            activeforeground=self._TEXT,
            relief="flat",
            bd=0,
            font=("Arial", 13, "bold"),
        )

    def _on_brightness_changed(self, value: str) -> None:
        brightness = int(float(value))
        self._brightness.set(brightness)
        self._brightness_text.set(f"{brightness}%")

        if self._brightness_after_id is not None:
            self.after_cancel(self._brightness_after_id)

        self._brightness_after_id = self.after(
            250,
            lambda b=brightness: self._submit(
                self._lighting.set_brightness(b),
                success_message=f"Brightness: {b}%",
            ),
        )

    def _on_pattern_selected(self) -> None:
        selected = self._pattern_name.get()
        for name, index in self._PATTERNS:
            if name == selected:
                self._submit(
                    self._lighting.set_pattern(index),
                    success_message=f"Effect: {name}",
                )
                return

    def _on_music_selected(self) -> None:
        selected = self._music_name.get()
        for name, index in self._MUSIC_MODES:
            if name == selected:
                self._submit(
                    self._lighting.set_music_mode(index),
                    success_message=f"Music: {name}",
                )
                return

    def _set_pattern_by_name(self, name: str) -> None:
        self._pattern_name.set(name)
        self._on_pattern_selected()

    def _submit(
        self,
        future: Future[None],
        *,
        success_message: str,
        failure_prefix: str = "Lighting error",
    ) -> None:
        self._set_status("Working...", self._MUTED_TEXT)
        future.add_done_callback(
            lambda completed: self.after(
                0,
                lambda: self._on_command_done(
                    completed,
                    success_message=success_message,
                    failure_prefix=failure_prefix,
                ),
            )
        )

    def _on_command_done(
        self,
        future: Future[None],
        *,
        success_message: str,
        failure_prefix: str,
    ) -> None:
        try:
            future.result()
        except Exception as exc:
            self._set_status(f"{failure_prefix}: {exc}", self._ERROR)
        else:
            status = "● " + success_message
            self._set_status(status, self._OK)

    def _set_status(self, text: str, color: str) -> None:
        self._status.set(text)
        if self._status_label is not None:
            self._status_label.configure(fg=color)

    def destroy(self) -> None:
        if self._brightness_after_id is not None:
            self.after_cancel(self._brightness_after_id)
            self._brightness_after_id = None

        try:
            self._lighting.disconnect()
        except Exception:
            pass

        super().destroy()
