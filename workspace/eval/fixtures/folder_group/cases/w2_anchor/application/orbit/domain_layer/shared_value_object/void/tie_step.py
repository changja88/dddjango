"""tie_step 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TieStep:
    value: str
