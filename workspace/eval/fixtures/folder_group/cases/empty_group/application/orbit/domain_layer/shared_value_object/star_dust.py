"""값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class StarDust:
    value: str
