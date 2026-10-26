"""tie_break_step 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TieBreakStep:
    value: str
