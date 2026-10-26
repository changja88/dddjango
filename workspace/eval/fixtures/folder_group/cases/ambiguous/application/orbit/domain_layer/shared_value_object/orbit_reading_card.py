"""orbit_reading_card 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class OrbitReadingCard:
    value: str
