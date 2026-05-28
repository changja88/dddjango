from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrderRequest:
    product_id: int
    quantity: int

