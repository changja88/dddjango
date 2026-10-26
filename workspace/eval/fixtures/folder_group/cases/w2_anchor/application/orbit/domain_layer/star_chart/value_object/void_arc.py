"""void_arc 값."""
from dataclasses import dataclass
from application.orbit.domain_layer.shared_value_object.void.half_step import HalfStep


@dataclass(frozen=True)
class VoidArc:
    value: str
