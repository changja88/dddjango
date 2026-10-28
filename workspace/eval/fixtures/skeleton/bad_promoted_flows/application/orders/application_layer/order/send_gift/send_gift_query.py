from dataclasses import dataclass


@dataclass(frozen=True)
class SendGiftQuery:
    target_id: int
