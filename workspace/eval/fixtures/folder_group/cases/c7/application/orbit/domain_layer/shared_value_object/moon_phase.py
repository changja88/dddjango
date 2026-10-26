"""moon_phase 값."""
from dataclasses import dataclass
from .half_span import HalfSpan


@dataclass(frozen=True)
class MoonPhase:
    value: str
