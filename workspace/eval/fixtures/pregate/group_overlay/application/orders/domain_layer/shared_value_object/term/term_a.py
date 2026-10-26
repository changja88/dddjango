"""term_a 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TermA:
    value: str
