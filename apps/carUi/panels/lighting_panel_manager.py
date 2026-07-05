from apps.carUi.panels.panel_manager_if import PanelManagerIf
from apps.carUi.panels.lighting_panel   import LightingPanel


class LightingPanelManager(PanelManagerIf):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.lighting_panel: LightingPanel | None = None

    def show(self) -> None:
        if not self.prepare_panel("Lighting"):
            return

        panel = LightingPanel(
            parent=self.content_frame,
            lighting_controller=self.app.lighting_controller,
        )

        panel.pack(fill="both", expand=True)
        self.lighting_panel = panel
        self.app.set_panel_title("Lighting Controls")
