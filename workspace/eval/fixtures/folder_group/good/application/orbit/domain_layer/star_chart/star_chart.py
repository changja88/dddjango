"""star_chart 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class StarChart:
    value: str
