from __future__ import annotations

import os
from pathlib import Path

from apps.carUi.runtime.radio_runtime_factory import create_car_ui_runtime
from apps.carUi.runtime.spotify_runtime_factory import (
    create_spotify_controller,
)
from apps.carUi.uiControlPanel import UiControlPanel
from apps.common.uiTheme.uiTheme import CAR_UI_THEME
from controllers.audio.pipewire_audio_controller import (
    PipewireAudioController,
)
from controllers.lighting.adapters.leddmx_bluetooth_controller import LedDmxBluetoothController
from controllers.lighting.parsers.leddmx_config_parser import load_leddmx_config
from hardware_io.gps.gps_reader import GpsReader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_CONFIG_PATH = (
    PROJECT_ROOT
    / "apps"
    / "carUi"
    / "config"
    / "car_ui_runtime.toml"
)


def main() -> None:
    runtime = create_car_ui_runtime(
        RUNTIME_CONFIG_PATH,
        project_root=PROJECT_ROOT,
    )

    gps_reader = GpsReader()
    audio_controller = PipewireAudioController(
        steps=CAR_UI_THEME["layout"]["volume_steps"],
    )
    spotify_controller = create_spotify_controller()
    lighting_controller = LedDmxBluetoothController(
        address=os.getenv("CARUI_LIGHTING_ADDRESS"),
        config=load_leddmx_config(project_root=PROJECT_ROOT),
    )

    app = UiControlPanel(
        runtime=runtime,
        gps_device=gps_reader,
        lighting_controller=lighting_controller,
        audio_controller=audio_controller,
        spotify_controller=spotify_controller,
    )

    try:
        app.register_default_callbacks()
        app.start_gps_ui_updates()
        app.mainloop()
    finally:
        gps_reader.close()
        lighting_controller.close()


if __name__ == "__main__":
    main()
