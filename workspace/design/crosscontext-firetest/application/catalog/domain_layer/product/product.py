from dataclasses import dataclass

from application.catalog.domain_layer.product.exceptions import OutOfStock


@dataclass
class Product:
    id: int
    stock: int

    def deduct(self, quantity: int) -> None:
        if self.stock < quantity:
            raise OutOfStock(f"stock {self.stock}, requested {quantity}")
        self.stock -= quantity
