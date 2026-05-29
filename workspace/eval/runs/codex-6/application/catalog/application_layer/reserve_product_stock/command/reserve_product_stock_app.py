from dataclasses import dataclass

from application.catalog.application_layer.reserve_product_stock.dto.reserve_product_stock_command import (
    ReserveProductStockCommand,
)
from application.catalog.domain_layer.product.repository.product_repository import (
    ProductRepository,
)


class ProductNotFound(Exception):
    def __init__(self, product_id: int) -> None:
        super().__init__(f"Product {product_id} was not found.")
        self.product_id = product_id


class StockReservationConflict(Exception):
    pass


@dataclass(frozen=True)
class ReserveProductStockResult:
    product_id: int
    stock: int


class ReserveProductStockApp:
    def __init__(self, repository: ProductRepository, max_attempts: int = 3) -> None:
        self._repository = repository
        self._max_attempts = max_attempts

    def reserve(self, command: ReserveProductStockCommand) -> ReserveProductStockResult:
        for _ in range(self._max_attempts):
            product = self._repository.get(command.product_id)
            if product is None:
                raise ProductNotFound(command.product_id)

            product.reserve(command.quantity)

            if self._repository.save(product):
                return ReserveProductStockResult(
                    product_id=product.id,
                    stock=product.stock,
                )

        raise StockReservationConflict("Stock changed during reservation.")
