from contextlib import AbstractContextManager, nullcontext
from dataclasses import dataclass
from typing import Callable

from django.db import OperationalError

from application.catalog.application_layer.reserve_stock.dto.reserve_product_stock_command import (
    ReserveProductStockCommand,
)
from application.catalog.domain_layer.product.repository.product_repository import (
    ConcurrentProductUpdate,
    ProductNotFound,
    ProductRepository,
)


@dataclass(frozen=True)
class ReserveProductStockResult:
    product_id: int
    stock: int


class StockReservationConflict(Exception):
    def __init__(self, product_id: int) -> None:
        self.product_id = product_id
        super().__init__(
            "The stock reservation could not be completed because the product was "
            "modified concurrently."
        )


class ReserveProductStockApp:
    def __init__(
        self,
        repository: ProductRepository,
        max_attempts: int = 3,
        transaction_context: Callable[[], AbstractContextManager] = nullcontext,
    ) -> None:
        self.repository = repository
        self.max_attempts = max_attempts
        self.transaction_context = transaction_context

    def reserve(
        self, command: ReserveProductStockCommand
    ) -> ReserveProductStockResult:
        for _attempt in range(self.max_attempts):
            try:
                with self.transaction_context():
                    loaded_product = self.repository.get(command.product_id)
                    product = loaded_product.product
                    product.reserve(command.quantity)
                    self.repository.save(
                        product=product,
                        expected_version=loaded_product.version,
                    )
                    return ReserveProductStockResult(
                        product_id=product.id,
                        stock=product.stock,
                    )
            except ConcurrentProductUpdate:
                continue
            except OperationalError as error:
                if _is_sqlite_database_locked(error):
                    continue
                raise

        raise StockReservationConflict(command.product_id)


def _is_sqlite_database_locked(error: OperationalError) -> bool:
    message = str(error).lower()
    return "database is locked" in message or "database table is locked" in message


__all__ = [
    "ConcurrentProductUpdate",
    "ProductNotFound",
    "ReserveProductStockApp",
    "ReserveProductStockResult",
    "StockReservationConflict",
]
