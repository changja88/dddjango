"""orbit_reading_spread 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class OrbitReadingSpread:
    value: str
