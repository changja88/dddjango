"""relation_link 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RelationLink:
    value: str
