"""term_end 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TermEnd:
    value: str
