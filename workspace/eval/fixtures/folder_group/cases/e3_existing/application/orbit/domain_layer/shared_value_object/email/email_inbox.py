"""email_inbox 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EmailInbox:
    value: str
