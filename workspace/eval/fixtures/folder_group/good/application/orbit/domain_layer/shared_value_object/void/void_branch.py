"""void_branch 값."""
from dataclasses import dataclass
from .tie_break_step import TieBreakStep


@dataclass(frozen=True)
class VoidBranch:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("value")
