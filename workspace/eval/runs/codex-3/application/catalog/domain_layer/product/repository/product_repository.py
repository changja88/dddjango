from typing import Protocol

from application.catalog.domain_layer.product.value_object.accepted_stock import (
    AcceptedStock,
)


class ProductRepository(Protocol):
    def accept_stock(self, product_id: int, quantity: int) -> AcceptedStock:
        ...
