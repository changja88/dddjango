"""star_chart 애그리거트 루트."""
from dataclasses import dataclass

from .event.star_chart_drawn import StarChartDrawn


@dataclass
class StarChart:
    star_chart_id: int
    value: str

    def draw(self) -> StarChartDrawn:
        return StarChartDrawn(self.value)
