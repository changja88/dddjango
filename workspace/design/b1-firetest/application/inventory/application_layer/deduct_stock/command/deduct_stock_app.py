from application.inventory.domain_layer.product.exceptions import InsufficientStock
from application.inventory.infra_layer.repository.product_repository import (
    ProductRepository,
)


class DeductStockApp:
    """Use case: deduct stock for a single product."""

    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self, product_id: int, quantity: int) -> None:
        applied = self._repository.deduct_stock(product_id, quantity)
        if not applied:
            raise InsufficientStock(
                f"could not deduct {quantity} from product {product_id}"
            )
