"""phase_shift 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseShift:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("value")
