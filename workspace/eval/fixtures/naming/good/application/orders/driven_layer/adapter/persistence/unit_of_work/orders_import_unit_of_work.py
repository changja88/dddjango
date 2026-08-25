from __future__ import annotations

from django.db import transaction

from application.orders.application_layer.port.unit_of_work.orders_import_unit_of_work import (
    OrdersImportUnitOfWork,
)


class DjangoOrdersImportUnitOfWork(OrdersImportUnitOfWork):
    """기술 접두(Django) + 역할 수식어(Import) 구현 — 판정 ① 양성."""

    def __enter__(self) -> "DjangoOrdersImportUnitOfWork":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False

    def after_commit(self, callback: object) -> None:
        transaction.on_commit(callback, robust=True)
