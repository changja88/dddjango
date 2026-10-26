"""void_ring 값."""
from dataclasses import dataclass
from ...shared_value_object.void.tie_step import TieStep


@dataclass(frozen=True)
class VoidRing:
    value: str
