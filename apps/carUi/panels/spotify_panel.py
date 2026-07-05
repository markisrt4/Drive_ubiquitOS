import tkinter as tk

from apps.common.uiTheme import COLORS, FONTS
from modules.media.spotify.spotify_controller import SpotifyController
from modules.media.spotify.spotify_state      import SpotifyState


class SpotifyPanel(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        controller: SpotifyController,
        on_back,
        compact_ui: bool = False,
    ) -> None:
        super().__init__(parent, bg=COLORS["app_bg"])

        self._controller = controller
        self._on_back = on_back
        self._compact_ui = compact_ui
        self._refresh_job: str | None = None

        self._track_var = tk.StringVar(value="--")
        self._artist_var = tk.StringVar(value="--")
        self._album_var = tk.StringVar(value="--")
        self._device_var = tk.StringVar(value="Device: --")
        self._status_var = tk.StringVar(value="Spotify")
        self._progress_var = tk.StringVar(value="--:-- / --:--")
        self._volume_var = tk.StringVar(value="Volume: --%")

        self._build_ui()

    def start(self) -> None:
        self._refresh()

    def stop(self) -> None:
        if self._refresh_job is not None:
            self.after_cancel(self._refresh_job)
            self._refresh_job = None

    def _on_progress_click(self, event) -> None:
        state = self._controller.current_state()

        if state.duration_ms is None or state.duration_ms <= 0:
            return

        width = max(1, self._progress_canvas.winfo_width())
        ratio = max(0.0, min(1.0, event.x / width))
        position_ms = int(state.duration_ms * ratio)

        try:
            self._controller.seek_to_position_ms(position_ms)
        except Exception as ex:
            self._status_var.set("Seek failed")
            print(f"[SpotifyPanel] Seek failed: {ex}")
            return

        self._apply_state(self._controller.current_state())

    def _build_ui(self) -> None:
        pad = 8 if self._compact_ui else 14

        header = tk.Frame(self, bg=COLORS["app_bg"])
        header.pack(fill="x", padx=pad, pady=(pad, 4))

        tk.Label(
            header,
            text="SPOTIFY",
            bg=COLORS["app_bg"],
            fg=COLORS["tile_title"],
            font=FONTS["tile_title"],
            anchor="w",
        ).pack(side="left")

        tk.Label(
            header,
            textvariable=self._status_var,
            bg=COLORS["app_bg"],
            fg=COLORS["status_telemetry_value"],
            font=FONTS["status"],
            anchor="e",
        ).pack(side="right")

        card = tk.Frame(
            self,
            bg=COLORS["tile_bg"],
            highlightthickness=2,
            highlightbackground=COLORS["tile_border"],
        )
        card.pack(fill="both", expand=True, padx=pad, pady=pad)

        tk.Label(
            card,
            textvariable=self._track_var,
            bg=COLORS["tile_bg"],
            fg=COLORS["tile_title"],
            font=(FONTS["tile_title"][0], 26 if self._compact_ui else 34, "bold"),
            anchor="center",
            wraplength=700,
        ).pack(fill="x", padx=14, pady=(18, 4))

        tk.Label(
            card,
            textvariable=self._artist_var,
            bg=COLORS["tile_bg"],
            fg=COLORS["tile_subtitle"],
            font=(FONTS["tile_subtitle"][0], 16 if self._compact_ui else 20),
            anchor="center",
            wraplength=700,
        ).pack(fill="x", padx=14)

        tk.Label(
            card,
            textvariable=self._album_var,
            bg=COLORS["tile_bg"],
            fg=COLORS["tile_detail"],
            font=FONTS["tile_detail"],
            anchor="center",
            wraplength=700,
        ).pack(fill="x", padx=14, pady=(2, 10))

        self._progress_canvas = tk.Canvas(
            card,
            height=18,
            bg=COLORS["tile_bg"],
            highlightthickness=0,
        )
        self._progress_canvas.pack(fill="x", padx=28, pady=(8, 2))

        self._progress_canvas.bind("<Button-1>", self._on_progress_click)
        self._progress_canvas.bind("<B1-Motion>", self._on_progress_click)

        tk.Label(
            card,
            textvariable=self._progress_var,
            bg=COLORS["tile_bg"],
            fg=COLORS["tile_detail"],
            font=FONTS["tile_detail"],
            anchor="center",
        ).pack(fill="x", padx=14, pady=(0, 10))

        controls = tk.Frame(card, bg=COLORS["tile_bg"])
        controls.pack(pady=(4, 12))

        self._button(
            controls,
            "⏮",
            self._previous,
            width=5,
        ).pack(side="left", padx=8)

        self._play_button = self._button(
            controls,
            "⏯",
            self._play_pause,
            width=5,
        )
        self._play_button.pack(side="left", padx=8)

        self._button(
            controls,
            "⏭",
            self._next,
            width=5,
        ).pack(side="left", padx=8)

        bottom = tk.Frame(card, bg=COLORS["tile_bg"])
        bottom.pack(fill="x", padx=18, pady=(4, 12))

        tk.Label(
            bottom,
            textvariable=self._device_var,
            bg=COLORS["tile_bg"],
            fg=COLORS["tile_subtitle"],
            font=FONTS["status"],
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        vol_frame = tk.Frame(bottom, bg=COLORS["tile_bg"])
        vol_frame.pack(side="right")

        self._button(vol_frame, "−", self._volume_down, width=3).pack(side="left", padx=3)

        tk.Label(
            vol_frame,
            textvariable=self._volume_var,
            bg=COLORS["tile_bg"],
            fg=COLORS["tile_subtitle"],
            font=FONTS["status"],
            width=13,
        ).pack(side="left", padx=3)

        self._button(vol_frame, "+", self._volume_up, width=3).pack(side="left", padx=3)

    def _button(
        self,
        parent: tk.Widget,
        text: str,
        command,
        width: int,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            bg=COLORS["volume_button_bg"],
            fg=COLORS["volume_button_fg"],
            activebackground=COLORS["top_bar_active"],
            activeforeground=COLORS["top_bar_fg"],
            font=FONTS["volume_button"],
            bd=0,
            relief="flat",
            cursor="hand2",
        )

    def _refresh(self) -> None:
        state = self._controller.current_state()
        self._apply_state(state)
        self._refresh_job = self.after(1000, self._refresh)

    def _apply_state(self, state: SpotifyState) -> None:
        self._status_var.set(state.status_message)
        self._track_var.set(state.track_name or "--")
        self._artist_var.set(state.artist_name or "--")
        self._album_var.set(state.album_name or "--")
        self._device_var.set(f"Device: {state.device_name or '--'}")

        if state.volume_percent is None:
            self._volume_var.set("Volume: --%")
        else:
            self._volume_var.set(f"Volume: {state.volume_percent}%")

        if state.is_playing:
            self._play_button.configure(text="⏸")
        else:
            self._play_button.configure(text="▶")

        self._progress_var.set(
            f"{self._format_ms(state.progress_ms)} / {self._format_ms(state.duration_ms)}"
        )
        self._draw_progress(state.progress_percent)

    def _draw_progress(self, progress_percent: float | None) -> None:
        self._progress_canvas.delete("all")

        width = self._progress_canvas.winfo_width()
        height = 18

        if width <= 1:
            width = 500

        self._progress_canvas.create_rectangle(
            0,
            6,
            width,
            12,
            fill=COLORS["tile_border"],
            outline="",
        )

        if progress_percent is None:
            return

        fill_width = width * max(0.0, min(100.0, progress_percent)) / 100.0

        self._progress_canvas.create_rectangle(
            0,
            6,
            fill_width,
            12,
            fill=COLORS["tile_accent"],
            outline="",
        )

    def _play_pause(self) -> None:
        self._controller.play_pause()
        self._apply_state(self._controller.current_state())

    def _next(self) -> None:
        self._controller.next_track()
        self._apply_state(self._controller.current_state())

    def _previous(self) -> None:
        self._controller.previous_track()
        self._apply_state(self._controller.current_state())

    def _volume_up(self) -> None:
        state = self._controller.current_state()
        current = state.volume_percent if state.volume_percent is not None else 50

        try:
            self._controller.set_volume_percent(current + 5)
        except Exception as ex:
            self._status_var.set("Volume control not supported")
            print(f"[SpotifyPanel] Volume up failed: {ex}")
            return

        self._apply_state(self._controller.current_state())


    def _volume_down(self) -> None:
        state = self._controller.current_state()
        current = state.volume_percent if state.volume_percent is not None else 50

        try:
            self._controller.set_volume_percent(current - 5)
        except Exception as ex:
            self._status_var.set("Volume control not supported")
            print(f"[SpotifyPanel] Volume down failed: {ex}")
            return

        self._apply_state(self._controller.current_state())

    @staticmethod
    def _format_ms(value: int | None) -> str:
        if value is None:
            return "--:--"

        total_seconds = max(0, value // 1000)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"
