from __future__ import annotations

from typing import Optional

from apps.carUi.panels.aircraft_panel import AircraftPanel
from apps.carUi.panels.panel_manager_if import PanelManagerIf
from apps.carUi.radio.radio_panel import RadioPanel
from apps.carUi.radio.radio_panel_config import (
    RadioPanelConfig,
    RadioPanelTileConfig,
)
from apps.carUi.radio.radio_panel_factory import create_radio_panel_binding
from apps.carUi.radio.radio_session_controller import RadioSessionController
from apps.common.uiTheme import AIRCRAFT_PANEL_THEME


class AircraftPanelManager(PanelManagerIf):
    """Coordinate the Aircraft menu, ADS-B launcher, and Airband radio."""

    def __init__(self, app) -> None:
        super().__init__(app)
        self.airband_panel: Optional[RadioPanel] = None
        self.airband_session: Optional[RadioSessionController] = None

    def show(self) -> None:
        if not self.prepare_panel("Aircraft"):
            return

        self.app.top_bar.set_back_command(self.app.show_main_menu)

        panel = AircraftPanel(
            parent=self.content_frame,
            on_adsb_pressed=self.launch_adsb,
            on_airband_pressed=self.show_airband_am,
            create_tile=self.create_tile,
            theme=AIRCRAFT_PANEL_THEME,
        )
        panel.pack(fill="both", expand=True)

        self.set_status("Aircraft menu ready")

    def launch_adsb(self) -> None:
        launcher = self.app.runtime.adsb_launcher
        if launcher is None:
            self.set_status("ADS-B is disabled")
            return

        try:
            running = launcher.toggle(
                remote_display=self.remote_display,
                set_status=self.set_status,
            )
            self.set_status(
                "ADS-B dashboard launched"
                if running
                else "ADS-B dashboard stopped"
            )
        except Exception as exc:
            self.set_status(f"ADS-B toggle failed: {exc}")
            print(f"[UI] ADS-B toggle error: {exc}")

    def show_airband_am(self) -> None:
        if not self.prepare_panel("Airband AM"):
            return

        self.app.top_bar.set_back_command(self.show)
        runtime = self.app.runtime.radios.get("airband")

        panel_config = RadioPanelConfig(
            key=runtime.key,
            title="Airband AM",
            launch_tile=RadioPanelTileConfig(
                label="Launch SDR++",
                subtitle="Airband AM receiver",
                detail="Starts / toggles SDR++",
            ),
            radio_toggle_tile=RadioPanelTileConfig(
                label="Radio ON/OFF",
                subtitle="Radio control",
                detail="Start / stop receiver",
            ),
            default_step_hz=runtime.config.default_mode.step_hz,
            default_mode_name=runtime.config.default_mode.name,
            preset_columns=2,
        )

        binding = create_radio_panel_binding(
            parent=self.content_frame,
            radio_controller=runtime.controller,
            radio_app_launcher=runtime.launcher,
            panel_config=panel_config,
            remote_display=self.remote_display,
            set_status=self.set_status,
            on_frequency_changed=(
                self.app.vehicle_status_manager.set_frequency
            ),
        )

        self.airband_session = binding.session
        self.airband_panel = binding.panel
        self.airband_panel.pack(fill="both", expand=True)
        self.airband_panel.start()
        self.airband_session.report_ready()

        self.app.top_bar.set_title("Airband AM Radio")
