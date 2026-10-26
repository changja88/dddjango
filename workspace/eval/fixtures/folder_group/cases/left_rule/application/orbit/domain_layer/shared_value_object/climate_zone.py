"""climate_zone 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ClimateZone:
    value: str
