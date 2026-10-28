from dataclasses import dataclass


@dataclass(frozen=True)
class SettlePaymentQuery:
    target_id: int
