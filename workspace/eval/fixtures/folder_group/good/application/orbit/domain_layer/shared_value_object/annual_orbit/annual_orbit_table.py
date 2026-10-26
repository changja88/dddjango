"""annual_orbit_table 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AnnualOrbitTable:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("value")
