"""chimes_scale 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ChimesScale:
    value: str
