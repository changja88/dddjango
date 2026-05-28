from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrderResult:
    order_id: int
    product_id: int
    quantity: int
    unit_price: int
    total_price: int
    remaining_stock: int

