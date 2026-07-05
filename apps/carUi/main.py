from pathlib import Path

from apps.carUi.uiControlPanel import UiControlPanel
from apps.carUi.config.radio_manifest_parser import RadioManifestParser
from apps.carUi.radio_runtime_assembly import assemble_radio_runtime
from modules.gps.gps_device import GPSDevice
from modules.lighting.leddmx.bluetooth_controller import LedDmxBluetoothController


def main() -> None:
    gps_device = GPSDevice()
    gps_device.start()

    app = UiControlPanel(remote_display=":2")
    app.gps_device = gps_device
    app.start_gps_ui_updates()

    app.lighting_controller = LedDmxBluetoothController(
        address="LEDDMX-00-043F",
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
