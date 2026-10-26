"""table_seat 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TableSeat:
    value: str
