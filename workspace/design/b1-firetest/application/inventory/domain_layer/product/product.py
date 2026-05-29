from dataclasses import dataclass

from application.inventory.domain_layer.product.exceptions import InsufficientStock


@dataclass
class Product:
    """A product with an on-hand stock level."""

    id: int
    stock: int

    def deduct(self, quantity: int) -> None:
        """Reduce stock by ``quantity`` when enough is on hand."""
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.stock < quantity:
            raise InsufficientStock(f"stock {self.stock} < requested {quantity}")
        self.stock -= quantity
