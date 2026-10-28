from dataclasses import dataclass


@dataclass(frozen=True)
class SettlePaymentResult:
    target_id: int
    done: bool
