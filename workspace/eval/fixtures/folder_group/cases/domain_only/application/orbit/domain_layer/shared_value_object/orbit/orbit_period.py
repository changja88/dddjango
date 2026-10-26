"""orbit_period 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class OrbitPeriod:
    value: str
