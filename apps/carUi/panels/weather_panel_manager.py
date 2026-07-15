from __future__ import annotations

from typing import Optional

from apps.carUi.panels.panel_manager_if import PanelManagerIf
from apps.carUi.panels.weather_panel import WeatherPanel
from apps.carUi.radio.radio_panel import RadioPanel
from apps.carUi.radio.radio_panel_config import (
    RadioPanelConfig,
    RadioPanelTileConfig,
)
from apps.carUi.radio.radio_panel_factory import (
    create_radio_panel_binding,
)
from apps.carUi.radio.radio_session_controller import (
    RadioSessionController,
)
from apps.common.uiTheme import WEATHER_PANEL_THEME


class WeatherPanelManager(PanelManagerIf):
    """Coordinate the weather dashboard and NOAA radio panel."""

    def __init__(self, app) -> None:
        super().__init__(app)
        self.noaa_panel: Optional[RadioPanel] = None
        self.noaa_session: Optional[RadioSessionController] = None

    def show(self) -> None:
        if not self.prepare_panel("Weather"):
            return

        self.app.top_bar.set_back_command(self.app.show_main_menu)

        weather_view = WeatherPanel(
            parent=self.content_frame,
            on_weather_dashboard_pressed=self.toggle_weather_dashboard,
            on_noaa_radio_pressed=self.show_noaa_weather_radio,
            create_tile=self.create_tile,
            theme=WEATHER_PANEL_THEME,
        )
        weather_view.pack(fill="both", expand=True)

        self.set_status("Weather menu ready")

    def toggle_weather_dashboard(self) -> None:
        launcher = self.app.runtime.weather_dash_launcher
        if launcher is None:
            self.set_status("Weather dashboard is disabled")
            return

        try:
            running = launcher.toggle(
                remote_display=self.remote_display,
                set_status=self.set_status,
            )
            self.set_status(
                "Weather dashboard launched"
                if running
                else "Weather dashboard stopped"
            )
        except Exception as exc:
            self.set_status(
                f"Weather dashboard toggle failed: {exc}"
            )
            print(f"[UI] Weather dashboard toggle error: {exc}")

    def show_noaa_weather_radio(self) -> None:
        if not self.prepare_panel("NOAA Weather Radio"):
            return

        self.app.top_bar.set_back_command(self.show)

        runtime = self.app.runtime.radios.get("weather_band")

        panel_config = RadioPanelConfig(
            key=runtime.key,
            title="NOAA Weather Radio",
            launch_tile=RadioPanelTileConfig(
                label="Launch SDR++",
                subtitle="NOAA receiver app",
                detail="Starts / toggles SDR++",
            ),
            radio_toggle_tile=RadioPanelTileConfig(
                label="Radio ON/OFF",
                subtitle="Weather band control",
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

        self.noaa_session = binding.session
        self.noaa_panel = binding.panel
        self.noaa_panel.pack(fill="both", expand=True)
        self.noaa_panel.start()
        self.noaa_session.report_ready()

        self.app.top_bar.set_title("NOAA Weather Radio")
