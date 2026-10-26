"""pillar_stem 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PillarStem:
    value: str
