"""moon_phase 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class MoonPhase:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("value")
