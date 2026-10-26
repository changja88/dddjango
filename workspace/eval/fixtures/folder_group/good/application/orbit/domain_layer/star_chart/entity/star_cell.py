"""star_cell 엔티티."""
from dataclasses import dataclass


@dataclass
class StarCell:
    star_cell_id: int
    value: str
