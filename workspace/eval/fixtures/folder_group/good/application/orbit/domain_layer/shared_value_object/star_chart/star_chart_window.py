"""star_chart_window 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class StarChartWindow:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("value")
