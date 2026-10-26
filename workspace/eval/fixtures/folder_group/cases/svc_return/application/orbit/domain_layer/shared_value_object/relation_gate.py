"""relation_gate 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RelationGate:
    value: str
