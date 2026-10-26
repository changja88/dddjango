"""orbit_void 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class OrbitVoid:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("value")
