"""term_window 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TermWindow:
    value: str
