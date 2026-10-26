"""void_pair 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VoidPair:
    value: str
