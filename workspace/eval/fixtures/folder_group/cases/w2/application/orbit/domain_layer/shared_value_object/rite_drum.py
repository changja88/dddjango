"""rite_drum 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RiteDrum:
    value: str
