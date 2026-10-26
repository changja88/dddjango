"""phase_angle 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseAngle:
    value: str
