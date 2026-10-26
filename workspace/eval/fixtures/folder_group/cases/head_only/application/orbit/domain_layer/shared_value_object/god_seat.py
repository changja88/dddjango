"""god_seat 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class GodSeat:
    value: str
