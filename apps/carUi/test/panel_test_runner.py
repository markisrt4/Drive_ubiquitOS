import argparse
import tkinter as tk
from types import SimpleNamespace

from apps.common.uiTheme import COLORS
from apps.carUi.top_bar import CarTopBar

from apps.carUi.panels.spotify_panel_manager import SpotifyPanelManager
from apps.carUi.panels.lighting_panel_manager import LightingPanelManager
from apps.carUi.panels.settings_panel_manager import SettingsPanelManager
from apps.carUi.panels.weather_panel_manager import WeatherPanelManager
from apps.carUi.panels.fm_radio_panel_manager import FMRadioPanelManager
from apps.carUi.panels.scanner_panel_manager import ScannerPanelManager
from apps.carUi.panels.aircraft_panel_manager import AircraftPanelManager

from modules.audio.audio_controller import AudioController
from modules.audio.pipewire_audio_controller import PipewireAudioController


class PanelTestApp(tk.Tk):
    def __init__(self, panel_name: str, geometry: str, fullscreen: bool) -> None:
        super().__init__()

        self.title(f"Panel Test: {panel_name}")
        self.geometry(geometry)
        self.attributes("-fullscreen", fullscreen)
        self.configure(bg=COLORS["app_bg"])

        self.compact_ui = self._geometry_is_compact(geometry)
        self.status_var = tk.StringVar(value=f"Testing panel: {panel_name}")

        self.audio_controller = AudioController(PipewireAudioController(steps=8))
        self.volume_level = self.audio_controller.get_volume_level()

        self._build_shell()
        self._build_panel_managers()
        self._show_panel(panel_name)

        self.bind("<Escape>", lambda event: self.destroy())

    @staticmethod
    def _geometry_is_compact(geometry: str) -> bool:
        try:
            size = geometry.split("+", 1)[0]
            width_text, height_text = size.lower().split("x", 1)
            width = int(width_text)
            height = int(height_text)
            return width <= 900 or height <= 520
        except Exception:
            return False

    def _build_shell(self) -> None:
        container = tk.Frame(self, bg=COLORS["app_bg"])
        container.pack(fill="both", expand=True)

        self.top_bar = CarTopBar(
            container,
            compact_ui=self.compact_ui,
            on_back=self.show_main_menu,
            on_volume_down=self.volume_down,
            on_volume_up=self.volume_up,
            on_power=self.destroy,
            on_settings=self._show_settings_placeholder,
            volume_level=self.volume_level,
            volume_steps=8,
        )
        self.top_bar.pack(fill="x", side="top")
        self.top_bar.set_back_command(self.destroy)
        self.top_bar.show_back_button()

        self.content_frame = tk.Frame(container, bg=COLORS["app_bg"])
        self.content_frame.pack(fill="both", expand=True, padx=8, pady=8)

        status = tk.Label(
            container,
            textvariable=self.status_var,
            anchor="w",
            bg=COLORS["status_bg"],
            fg=COLORS["status_fg"],
            padx=10,
            pady=4,
        )
        status.pack(fill="x", side="bottom")

    def _build_panel_managers(self) -> None:
        self.spotify_panel_manager = SpotifyPanelManager(self)
        self.lighting_panel_manager = LightingPanelManager(self)
        self.settings_panel_manager = SettingsPanelManager(self)
        self.weather_panel_manager = WeatherPanelManager(self)
        self.fm_radio_panel_manager = FMRadioPanelManager(self)
        self.scanner_panel_manager = ScannerPanelManager(self)
        self.aircraft_panel_manager = AircraftPanelManager(self)

        # Some panels may expect these to exist. Tiny fake object theater.
        self.callbacks = {}
        self.remote_display = ":2"
        self.gps_device = None
        self.lighting_controller = None

    def _show_panel(self, panel_name: str) -> None:
        panels = {
            "spotify": self.spotify_panel_manager.show,
            "lighting": self.lighting_panel_manager.show,
            "settings": self.settings_panel_manager.show,
            "weather": self.weather_panel_manager.show,
            "fm_radio": self.fm_radio_panel_manager.show,
            "scanner": self.scanner_panel_manager.show,
            "aircraft": self.aircraft_panel_manager.show,
        }

        show = panels.get(panel_name)
        if show is None:
            names = ", ".join(sorted(panels.keys()))
            raise ValueError(f"Unknown panel '{panel_name}'. Valid panels: {names}")

        show()

    def show_main_menu(self) -> None:
        self.destroy()

    def set_panel_title(self, title: str) -> None:
        self.top_bar.set_title(title)

    def set_current_frequency(self, frequency_hz: int | None) -> None:
        if frequency_hz is None:
            self.top_bar.set_frequency_text("--")
        else:
            self.top_bar.set_frequency_text(f"{frequency_hz / 1_000_000:.3f} MHz")

    def set_location(self, lat: float | None, lon: float | None) -> None:
        if lat is None or lon is None:
            self.top_bar.set_location_text("🌎 lat.--, lon.--")
        else:
            self.top_bar.set_location_text(f"🌎 lat.{lat:.4f}, lon.{lon:.4f}")

    def volume_up(self) -> None:
        self.volume_level = min(8, self.volume_level + 1)
        self.top_bar.set_volume_level(self.volume_level)

    def volume_down(self) -> None:
        self.volume_level = max(0, self.volume_level - 1)
        self.top_bar.set_volume_level(self.volume_level)

    def _clear_content(self) -> None:
        for child in self.content_frame.winfo_children():
            child.destroy()

    def _show_settings_placeholder(self) -> None:
        self.status_var.set("Settings not available in panel test runner")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch one Car UI panel for testing.")
    parser.add_argument(
        "panel",
        choices=[
            "spotify",
            "lighting",
            "settings",
            "weather",
            "fm_radio",
            "scanner",
            "aircraft",
        ],
    )
    parser.add_argument("--geometry", default="800x480")
    parser.add_argument("--fullscreen", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    app = PanelTestApp(
        panel_name=args.panel,
        geometry=args.geometry,
        fullscreen=args.fullscreen,
    )
    app.mainloop()


if __name__ == "__main__":
    main()
