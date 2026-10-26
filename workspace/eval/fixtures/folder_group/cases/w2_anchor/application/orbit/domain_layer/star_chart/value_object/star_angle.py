"""star_angle 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class StarAngle:
    value: str
