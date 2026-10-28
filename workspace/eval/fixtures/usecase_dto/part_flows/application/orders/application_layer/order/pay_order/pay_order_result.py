from dataclasses import dataclass


@dataclass(frozen=True)
class PayOrderResult:
    order_id: str
