from abc import ABC, abstractmethod
import tkinter as tk
from typing import Any


class PanelManagerIf(ABC):
    def __init__(self, app: Any) -> None:
        self.app = app

    @abstractmethod
    def show(self) -> None:
        pass

    def prepare_panel(self, title: str) -> bool:
        navigation = getattr(self.app, "navigation", None)
        if navigation is not None:
            navigation.clear_content()
        else:
            self.app._clear_content()

        self.set_title(title)
        self.app.top_bar.show_back_button()
        return True

    def set_title(self, title: str) -> None:
        if hasattr(self.app, "set_panel_title"):
            self.app.set_panel_title(title)
        else:
            self.app.top_bar.set_title(title)

    def set_status(self, message: str) -> None:
        status_bar = getattr(self.app, "status_bar", None)
        if status_bar is not None:
            status_bar.set_status(message)
        else:
            self.app.status_var.set(message)

    @property
    def content_frame(self) -> tk.Frame:
        return self.app.content_frame

    @property
    def remote_display(self) -> str:
        return self.app.remote_display

    def create_tile(
        self,
        parent: tk.Widget,
        key: str,
        label: str,
        subtitle: str,
        detail: str,
    ) -> tk.Frame:
        return self.app.create_subpanel_tile(parent, key, label, subtitle, detail)
