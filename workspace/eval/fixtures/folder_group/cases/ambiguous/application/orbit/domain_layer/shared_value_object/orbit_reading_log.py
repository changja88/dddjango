"""orbit_reading_log 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class OrbitReadingLog:
    value: str
