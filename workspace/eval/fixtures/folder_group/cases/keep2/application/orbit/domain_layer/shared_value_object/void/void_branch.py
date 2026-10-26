"""void_branch 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VoidBranch:
    value: str
