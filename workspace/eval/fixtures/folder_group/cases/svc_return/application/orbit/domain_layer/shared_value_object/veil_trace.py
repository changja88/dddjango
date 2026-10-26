"""veil_trace 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VeilTrace:
    value: str
