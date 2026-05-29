from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrderCommand:
    product_id: int
    quantity: int


@dataclass(frozen=True)
class CreateOrderResult:
    id: int
    product_id: int
    quantity: int
    status: str
