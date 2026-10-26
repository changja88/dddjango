"""climate_band 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ClimateBand:
    value: str
