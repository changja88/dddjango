"""값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class MoonPhase:
    value: str
