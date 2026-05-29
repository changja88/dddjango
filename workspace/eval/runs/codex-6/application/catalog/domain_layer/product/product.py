from dataclasses import dataclass

from application.catalog.domain_layer.product.exception import (
    InsufficientStock,
    InvalidReservationQuantity,
)


@dataclass
class Product:
    id: int
    stock: int
    version: int

    def reserve(self, quantity: int) -> None:
        if quantity <= 0:
            raise InvalidReservationQuantity(quantity)

        if self.stock < quantity:
            raise InsufficientStock(
                requested_quantity=quantity,
                available_stock=self.stock,
            )

        self.stock -= quantity
