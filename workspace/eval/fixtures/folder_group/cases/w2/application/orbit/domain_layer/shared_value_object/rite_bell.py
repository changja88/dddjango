"""rite_bell 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RiteBell:
    value: str
