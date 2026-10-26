"""void_gate 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VoidGate:
    value: str
