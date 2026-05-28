from types import TracebackType
from typing import Any, Optional, Type

from django.db import transaction

from application.catalog.infra_layer.repository.order_repository import (
    DjangoOrderRepository,
)
from application.catalog.infra_layer.repository.product_repository import (
    DjangoProductRepository,
)


class DjangoCatalogUnitOfWork:
    def __init__(self) -> None:
        self.product_repository = DjangoProductRepository()
        self.order_repository = DjangoOrderRepository()
        self._atomic: Any = None
        self._committed = False

    def __enter__(self) -> "DjangoCatalogUnitOfWork":
        self._atomic = transaction.atomic()
        self._atomic.__enter__()
        self._committed = False
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        if self._atomic is None:
            return False

        if exc_type is None and not self._committed:
            transaction.set_rollback(True)

        try:
            return self._atomic.__exit__(exc_type, exc_value, traceback)
        finally:
            self._atomic = None
            self._committed = False

    def commit(self) -> None:
        if self._atomic is None:
            raise RuntimeError("Unit of work has not been entered.")
        self._committed = True

    def rollback(self) -> None:
        if self._atomic is None:
            raise RuntimeError("Unit of work has not been entered.")
        transaction.set_rollback(True)
