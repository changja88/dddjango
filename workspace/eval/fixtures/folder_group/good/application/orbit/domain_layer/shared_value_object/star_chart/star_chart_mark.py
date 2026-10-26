"""star_chart_mark 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class StarChartMark:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("value")
