"""climate_god 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ClimateGod:
    value: str
