from dataclasses import dataclass


@dataclass(frozen=True)
class GetOrderRequest:
    order_id: str
