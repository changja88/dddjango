"""annual_orbit 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AnnualOrbit:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("value")
