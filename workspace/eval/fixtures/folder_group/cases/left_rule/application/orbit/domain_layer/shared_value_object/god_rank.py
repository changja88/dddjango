"""god_rank 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class GodRank:
    value: str
