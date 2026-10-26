"""void_b 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VoidB:
    value: str
