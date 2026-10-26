"""carried_request 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CarriedRequest:
    value: str
