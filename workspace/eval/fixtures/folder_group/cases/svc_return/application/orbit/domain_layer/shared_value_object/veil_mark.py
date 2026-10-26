"""veil_mark 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VeilMark:
    value: str
