"""request_carried 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestCarried:
    value: str
