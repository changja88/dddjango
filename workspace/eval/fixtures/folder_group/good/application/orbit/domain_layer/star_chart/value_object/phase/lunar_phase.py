"""lunar_phase 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class LunarPhase:
    value: str
