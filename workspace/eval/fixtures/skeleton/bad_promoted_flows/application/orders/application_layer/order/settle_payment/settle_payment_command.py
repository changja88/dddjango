from dataclasses import dataclass


@dataclass(frozen=True)
class SettlePaymentCommand:
    target_id: int
