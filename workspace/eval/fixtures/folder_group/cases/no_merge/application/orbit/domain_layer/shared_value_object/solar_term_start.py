"""solar_term_start 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SolarTermStart:
    value: str
