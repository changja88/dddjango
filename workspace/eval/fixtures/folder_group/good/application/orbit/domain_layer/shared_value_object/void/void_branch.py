"""void_branch 값."""
from dataclasses import dataclass
from .tie_break_step import TieBreakStep


@dataclass(frozen=True)
class VoidBranch:
    value: str
