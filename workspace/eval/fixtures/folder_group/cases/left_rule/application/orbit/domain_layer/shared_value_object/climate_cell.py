"""climate_cell 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ClimateCell:
    value: str
