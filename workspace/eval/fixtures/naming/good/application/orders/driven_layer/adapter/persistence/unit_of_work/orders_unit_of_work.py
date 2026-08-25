from __future__ import annotations

from django.db import transaction

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork


class DjangoOrdersUnitOfWork(OrdersUnitOfWork):
    def __enter__(self) -> "DjangoOrdersUnitOfWork":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False

    def after_commit(self, callback: object) -> None:
        transaction.on_commit(callback, robust=True)
