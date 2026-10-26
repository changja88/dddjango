"""star_chart_window 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class StarChartWindow:
    value: str
