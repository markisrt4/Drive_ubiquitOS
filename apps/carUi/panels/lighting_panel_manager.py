from __future__ import annotations

from typing import Optional

from apps.carUi.panels.lighting_panel import LightingPanel
from apps.carUi.panels.panel_manager_if import PanelManagerIf
from apps.common.uiTheme import LIGHTING_PANEL_THEME


class LightingPanelManager(PanelManagerIf):
    """Create and own the lighting control panel."""

    def __init__(self, app) -> None:
        super().__init__(app)
        self.lighting_panel: Optional[LightingPanel] = None

    def show(self) -> None:
        if not self.prepare_panel("Lighting"):
            return

        self.app.top_bar.set_title("Lighting Controls")

        panel = LightingPanel(
            parent=self.content_frame,
            lighting_controller=self.app.lighting_controller,
            theme=LIGHTING_PANEL_THEME,
        )
        panel.pack(fill="both", expand=True)

        self.lighting_panel = panel
        self.set_status("Lighting controls ready")
