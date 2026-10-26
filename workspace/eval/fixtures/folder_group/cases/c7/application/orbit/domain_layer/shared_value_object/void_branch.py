"""void_branch 값."""
from dataclasses import dataclass
from .tie_break_step import TieBreakStep
from .carried_request import CarriedRequest
from .half_span import HalfSpan


@dataclass(frozen=True)
class VoidBranch:
    value: str
