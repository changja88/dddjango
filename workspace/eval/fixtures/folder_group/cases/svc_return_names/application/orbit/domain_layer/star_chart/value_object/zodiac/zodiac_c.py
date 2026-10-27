"""zodiac_c 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ZodiacC:
    value: str
