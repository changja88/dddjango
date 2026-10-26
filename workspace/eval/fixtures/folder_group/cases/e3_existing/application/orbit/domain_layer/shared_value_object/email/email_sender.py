"""email_sender 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EmailSender:
    value: str
