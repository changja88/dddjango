"""pillar 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Pillar:
    value: str
