from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrderCommand:
    product_id: int
    quantity: int

