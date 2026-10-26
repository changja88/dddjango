"""star_chart_axis 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class StarChartAxis:
    value: str
