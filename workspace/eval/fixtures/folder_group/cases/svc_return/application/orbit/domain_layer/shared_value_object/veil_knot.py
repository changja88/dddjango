"""veil_knot 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VeilKnot:
    value: str
