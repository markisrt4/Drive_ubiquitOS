import tkinter as tk

from apps.carUi.panels.panel_manager_if import PanelManagerIf


class SettingsPanelManager(PanelManagerIf):
    def show(self) -> None:
        if not self.prepare_panel("Settings"):
            return

        grid = tk.Frame(self.content_frame, bg=self.app["app_bg"] if False else "#111418")
        grid.pack(fill="both", expand=True)

        for col in range(3):
            grid.columnconfigure(col, weight=1, uniform="settings_col")
        for row in range(2):
            grid.rowconfigure(row, weight=1, uniform="settings_row")

        tiles = [
            ("audio_aux", "AUX", "Audio output", "Use analog/aux output", self.select_aux),
            ("audio_hdmi", "HDMI", "Audio output", "Use HDMI audio", self.select_hdmi),
            ("audio_bt", "Bluetooth", "Audio output", "Choose paired device", self.show_bluetooth_devices),
            ("gps_hw", "Hardware GPS", "GPS source", "Use ttyACM0 / gpsd", self.select_hardware_gps),
            ("gps_sim", "Sim GPS", "GPS source", "Use simulated route", self.select_sim_gps),
            ("wifi", "Wi-Fi", "Network", "Choose Wi-Fi source", self.show_wifi_networks),
        ]

        for index, (key, label, subtitle, detail, callback) in enumerate(tiles):
            row = index // 3
            col = index % 3

            tile = self.create_tile(grid, key, label, subtitle, detail)
            tile.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
            self._bind_click_recursive(tile, callback)

        self.set_status("Settings ready")

    def _bind_click_recursive(self, widget, callback) -> None:
        widget.bind("<Button-1>", lambda event: callback())
        for child in widget.winfo_children():
            self._bind_click_recursive(child, callback)

    def select_aux(self) -> None:
        self.set_status("Audio output: AUX selected")

    def select_hdmi(self) -> None:
        self.set_status("Audio output: HDMI selected")

    def show_bluetooth_devices(self) -> None:
        self.set_status("Bluetooth device picker coming next")

    def select_hardware_gps(self) -> None:
        self.app.gps_source = "hardware"
        self.set_status("GPS source: hardware")

    def select_sim_gps(self) -> None:
        self.app.gps_source = "sim"
        self.set_status("GPS source: simulator")

    def show_wifi_networks(self) -> None:
        self.set_status("Wi-Fi picker coming next")
