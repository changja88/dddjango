"""useful_god 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class UsefulGod:
    value: str
