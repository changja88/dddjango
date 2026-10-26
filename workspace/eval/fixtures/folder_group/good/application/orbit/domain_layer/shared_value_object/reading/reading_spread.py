"""reading_spread 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ReadingSpread:
    value: str
