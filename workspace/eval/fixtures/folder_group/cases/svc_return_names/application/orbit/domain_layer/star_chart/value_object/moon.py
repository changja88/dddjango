"""moon 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Moon:
    value: str
