"""amber_bronze 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AmberBronze:
    value: str
