"""void_gate 값."""
from dataclasses import dataclass
from application.orbit.domain_layer.shared_value_object.tie_break_step import TieBreakStep


@dataclass(frozen=True)
class VoidGate:
    value: str
