"""table_lamp 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TableLamp:
    value: str
