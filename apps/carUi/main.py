from __future__ import annotations

import os
from pathlib import Path

from apps.carUi.config.radio_manifest_parser import RadioManifestParser
from apps.carUi.radio_runtime_assembly import assemble_radio_runtime
from apps.carUi.uiControlPanel import UiControlPanel
from modules.gps.gps_device import GPSDevice
from modules.lighting.leddmx.bluetooth_controller import LedDmxBluetoothController


def main() -> None:
    gps_device = GPSDevice()
    gps_device.start()

    app = UiControlPanel(remote_display=":2")
    app.gps_device = gps_device
    app.start_gps_ui_updates()

    # Optional. Leave unset to scan for the LEDDMX BLE service UUID.
    # Set this only if you know the controller exposes a stable BLE address.
    lighting_address = os.getenv("CARUI_LIGHTING_ADDRESS")
    app.lighting_controller = LedDmxBluetoothController(
        address=lighting_address,
    )

    radio_manifest_parser = RadioManifestParser(
        Path("apps/carUi/config/radio_manifest.json")
    )

    assemble_radio_runtime(
        app,
        radio_manifest_parser=radio_manifest_parser,
    )

    app.register_default_callbacks()
    app.mainloop()


if __name__ == "__main__":
    main()
