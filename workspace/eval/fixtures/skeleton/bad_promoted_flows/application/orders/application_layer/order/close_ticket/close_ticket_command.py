from dataclasses import dataclass


@dataclass(frozen=True)
class CloseTicketCommand:
    target_id: int
