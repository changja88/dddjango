"""half_span 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class HalfSpan:
    value: str
