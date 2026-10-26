"""chimes_ring 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ChimesRing:
    value: str
