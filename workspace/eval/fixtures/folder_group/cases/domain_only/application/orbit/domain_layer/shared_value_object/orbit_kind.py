"""orbit_kind 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class OrbitKind:
    value: str
