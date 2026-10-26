"""solar_term_gap 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SolarTermGap:
    value: str
