"""bronze_amber 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class BronzeAmber:
    value: str
