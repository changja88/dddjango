from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceOrderResult:
    order_id: str
    total: str
