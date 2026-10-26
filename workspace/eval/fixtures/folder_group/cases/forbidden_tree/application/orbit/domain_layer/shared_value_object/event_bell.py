"""event_bell 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EventBell:
    value: str
