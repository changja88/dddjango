"""term_gap 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TermGap:
    value: str
