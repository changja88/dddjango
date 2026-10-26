"""relation_seam 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RelationSeam:
    value: str
