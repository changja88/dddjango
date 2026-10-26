"""email_draft 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EmailDraft:
    value: str
