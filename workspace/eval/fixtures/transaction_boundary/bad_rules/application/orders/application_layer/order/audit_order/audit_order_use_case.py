"""#197 경계(음성) — 죽은 helper 방패 차단: 어디서도 안 닿는 `_legacy_txn` 의 with+save 는 불산입."""
from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork


class AuditOrderUseCase:
    def __init__(self, unit_of_work_factory: Callable[[], OrdersUnitOfWork]) -> None:
        self._unit_of_work_factory: Callable[[], OrdersUnitOfWork] = unit_of_work_factory

    def execute(self, order_id: str) -> str:
        return f"audited:{order_id}"

    def _legacy_txn(self, order: object) -> None:
        with self._unit_of_work_factory() as unit_of_work:
            unit_of_work.repository.save(order)
