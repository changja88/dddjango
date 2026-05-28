from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrderResponse:
    order_id: int
    product_id: int
    quantity: int
    unit_price: int
    total_price: int
    remaining_stock: int

    def to_dict(self) -> dict[str, int]:
        return {
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_price": self.total_price,
            "remaining_stock": self.remaining_stock,
        }

