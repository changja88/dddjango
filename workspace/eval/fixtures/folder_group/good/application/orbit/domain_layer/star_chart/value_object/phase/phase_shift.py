"""phase_shift 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseShift:
    value: str
