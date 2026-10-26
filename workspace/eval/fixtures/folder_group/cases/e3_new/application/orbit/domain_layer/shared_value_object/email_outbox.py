"""email_outbox 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EmailOutbox:
    value: str
