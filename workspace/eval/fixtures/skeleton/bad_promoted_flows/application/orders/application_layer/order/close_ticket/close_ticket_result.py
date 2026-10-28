from dataclasses import dataclass


@dataclass(frozen=True)
class CloseTicketResult:
    target_id: int
    done: bool
