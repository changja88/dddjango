from dataclasses import dataclass

from application.catalog.domain_layer.order.exception import (
    InvalidOrderQuantity,
    InvalidUnitPrice,
)


@dataclass(frozen=True)
class Order:
    product_id: int
    quantity: int
    unit_price: int

    @classmethod
    def create(cls, *, product_id: int, quantity: int, unit_price: int) -> "Order":
        if quantity < 1:
            raise InvalidOrderQuantity(quantity)
        if unit_price < 0:
            raise InvalidUnitPrice(unit_price)
        return cls(product_id=product_id, quantity=quantity, unit_price=unit_price)

    @property
    def total_price(self) -> int:
        return self.quantity * self.unit_price

