from dataclasses import dataclass


@dataclass(frozen=True)
class PayOrderCommand:
    order_id: str
