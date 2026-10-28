from dataclasses import dataclass


@dataclass(frozen=True)
class SendGiftCommand:
    target_id: int
