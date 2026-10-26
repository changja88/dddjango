"""request_pending 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestPending:
    value: str
