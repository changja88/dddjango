from dataclasses import dataclass

from application.catalog.domain_layer.product.exception import InsufficientStock
from application.catalog.domain_layer.product.value_object.reservation_quantity import (
    ReservationQuantity,
)


@dataclass
class Product:
    id: int
    name: str
    price: int
    stock: int

    def __post_init__(self) -> None:
        if self.stock < 0:
            raise ValueError("Product stock must not be negative.")

    def reserve(self, quantity: int) -> None:
        reservation_quantity = ReservationQuantity(quantity)
        if self.stock < reservation_quantity.value:
            raise InsufficientStock(
                product_id=self.id,
                requested_quantity=reservation_quantity.value,
                available_stock=self.stock,
            )
        self.stock -= reservation_quantity.value

