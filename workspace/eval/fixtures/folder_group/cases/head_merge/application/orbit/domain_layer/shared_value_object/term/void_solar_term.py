"""void_solar_term 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VoidSolarTerm:
    value: str
