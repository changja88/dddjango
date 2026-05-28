from types import TracebackType
from typing import Optional, Protocol, Type

from application.catalog.domain_layer.order.repository.order_repository import (
    OrderRepository,
)
from application.catalog.domain_layer.product.repository.product_repository import (
    ProductRepository,
)


class CatalogUnitOfWork(Protocol):
    product_repository: ProductRepository
    order_repository: OrderRepository

    def __enter__(self) -> "CatalogUnitOfWork":
        ...

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
