from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceOrderCommand:
    order_id: str
    quantity: int
