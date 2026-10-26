"""event_gong 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EventGong:
    value: str
