"""값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ZodiacA:
    value: str
