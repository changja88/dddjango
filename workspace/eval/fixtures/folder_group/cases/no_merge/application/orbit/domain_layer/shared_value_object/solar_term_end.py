"""solar_term_end 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SolarTermEnd:
    value: str
