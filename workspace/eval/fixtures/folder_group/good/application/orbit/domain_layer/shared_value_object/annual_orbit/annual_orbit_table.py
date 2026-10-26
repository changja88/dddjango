"""annual_orbit_table 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AnnualOrbitTable:
    value: str
