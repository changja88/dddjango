from collections.abc import Callable
from typing import TypeVar

from django.db import OperationalError, connection, transaction

from application.orders.domain_layer.order.port.product_inventory_port import (
    InventoryConflict,
)


ResultT = TypeVar("ResultT")


class DjangoTransactionRunner:
    def run(self, operation: Callable[[], ResultT]) -> ResultT:
        try:
            with transaction.atomic():
                return operation()
        except OperationalError as exc:
            if _is_sqlite_lock_error(exc):
                raise InventoryConflict("inventory database conflict") from exc
            raise


def _is_sqlite_lock_error(exc: OperationalError) -> bool:
    if connection.vendor != "sqlite":
        return False

    message = str(exc).lower()
    return any(
        lock_message in message
        for lock_message in (
            "database is locked",
            "database table is locked",
            "database schema is locked",
        )
    )
