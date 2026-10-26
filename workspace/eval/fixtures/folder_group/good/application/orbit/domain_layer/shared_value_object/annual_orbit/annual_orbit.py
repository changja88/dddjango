"""annual_orbit 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AnnualOrbit:
    value: str
