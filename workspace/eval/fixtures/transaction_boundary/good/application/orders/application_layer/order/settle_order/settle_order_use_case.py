"""#197 측정 정밀화 경계 — factory 호출형 with + `uow.repository.save()` 수신자형 쓰기 인정."""
from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork


class SettleOrderUseCase:
    def __init__(self, unit_of_work_factory: Callable[[], OrdersUnitOfWork]) -> None:
        self._unit_of_work_factory: Callable[[], OrdersUnitOfWork] = unit_of_work_factory

    def execute(self, order_id: str) -> None:
        with self._unit_of_work_factory() as unit_of_work:
            order = unit_of_work.repository.get(order_id)
            order.settle()
            unit_of_work.repository.save(order)
