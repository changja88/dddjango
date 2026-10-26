"""chimes_tone 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ChimesTone:
    value: str
