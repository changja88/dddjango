"""phase_kind 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseKind:
    value: str
