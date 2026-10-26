"""void_state 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VoidState:
    value: str
