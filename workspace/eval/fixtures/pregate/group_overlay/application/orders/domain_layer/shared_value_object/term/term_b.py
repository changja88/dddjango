"""term_b 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TermB:
    value: str
