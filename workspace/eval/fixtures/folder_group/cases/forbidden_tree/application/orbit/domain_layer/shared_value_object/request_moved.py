"""request_moved 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestMoved:
    value: str
