"""hour_pillar 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class HourPillar:
    value: str
