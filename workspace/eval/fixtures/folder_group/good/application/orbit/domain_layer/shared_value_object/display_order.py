"""display_order 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DisplayOrder:
    value: str
