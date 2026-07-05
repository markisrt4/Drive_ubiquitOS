import tkinter as tk
from collections.abc import Mapping

from apps.common.instruments.gauge_config import GaugeConfig
from apps.common.instruments.gauge_style  import GaugeStyle
from apps.common.instruments.gauge_widget import GaugeWidget


class InstrumentPanel(tk.Frame):
    def __init__(
        self,
        parent,
        gauges: Mapping[str, GaugeConfig],
        columns: int = 3,
        style: GaugeStyle | None = None,
    ) -> None:
        self._style = style or GaugeStyle()

        super().__init__(parent, bg=self._style.background)

        self._gauges: dict[str, GaugeWidget] = {}

        for index, (name, config) in enumerate(gauges.items()):
            gauge = GaugeWidget(self, config, self._style)
            row = index // columns
            column = index % columns
            gauge.grid(row=row, column=column, padx=8, pady=8)
            self._gauges[name] = gauge

    def set_value(self, name: str, value: float | None) -> None:
        gauge = self._gauges.get(name)

        if gauge is None:
            return

        gauge.set_value(value)

    def set_values(self, values: Mapping[str, float | None]) -> None:
        for name, value in values.items():
            self.set_value(name, value)
