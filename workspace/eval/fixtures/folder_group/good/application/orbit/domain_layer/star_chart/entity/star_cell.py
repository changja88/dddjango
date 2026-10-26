"""star_cell 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class StarCell:
    value: str
