# PiRF Radio Panel Manager

Files:

```text
apps/carUi/radio_panel_manager.py
modules/sdr/sdrpp_app_launcher.py
```

Example wiring:

```python
from apps.carUi.radio_panel_manager import (
    RadioPanelManager,
    RadioPanelConfig,
    RadioPanelTileConfig,
)
from modules.sdr.sdrpp_app_launcher import SDRPPAppLauncher
from modules.sdrpp_launcher import FM_BROADCAST_PROFILE

fm_panel_manager = RadioPanelManager(
    parent=self.content_frame,
    create_tile=self.create_subpanel_tile,
    radio_controller=self.fm_radio_controller,
    radio_app_launcher=SDRPPAppLauncher(FM_BROADCAST_PROFILE),
    panel_config=RadioPanelConfig(
        key="fm_radio",
        title="FM Radio",
        launch_tile=RadioPanelTileConfig(
            label="Toggle SDR++",
            subtitle="FM receiver app",
            detail="Launch / stop SDR++",
        ),
        radio_toggle_tile=RadioPanelTileConfig(
            label="Radio ON/OFF",
            subtitle="Radio control",
            detail="Start / stop receiver",
        ),
        default_step_hz=100_000,
        default_mode_name="WFM",
        preset_columns=2,
    ),
    remote_display=self.remote_display,
    set_status=self.status_var.set,
)

fm_panel_manager.show()
```
