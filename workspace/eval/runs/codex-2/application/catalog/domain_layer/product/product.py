from dataclasses import dataclass

from application.catalog.domain_layer.product.exception import (
    InsufficientStock,
    InvalidReserveQuantity,
)


@dataclass
class Product:
    id: int
    name: str
    price: int
    stock: int

    def reserve(self, quantity: int) -> None:
        if quantity < 1:
            raise InvalidReserveQuantity(quantity)
        if self.stock < quantity:
            raise InsufficientStock(
                product_id=self.id,
                requested_quantity=quantity,
                available_stock=self.stock,
            )
        self.stock -= quantity

