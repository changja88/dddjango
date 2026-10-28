from dataclasses import dataclass


@dataclass(frozen=True)
class CloseTicketQuery:
    target_id: int
