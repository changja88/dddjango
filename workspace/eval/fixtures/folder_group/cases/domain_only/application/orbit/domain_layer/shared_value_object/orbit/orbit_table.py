"""orbit_table 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class OrbitTable:
    value: str
