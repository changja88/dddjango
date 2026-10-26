"""star_chart_mark 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class StarChartMark:
    value: str
