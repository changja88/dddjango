"""#197 측정 정밀화 경계 — 2단 헬퍼 사슬의 쓰기 도달(kkebi recover 판형: execute→_process→_persist)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository


class RecoverOrderUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_id: str) -> bool:
        return self._process(order_id)

    def _process(self, order_id: str) -> bool:
        with self._unit_of_work:
            order = self._repository.get(order_id)
        if order is None:
            return False
        return self._persist(order)

    def _persist(self, order: object) -> bool:
        with self._unit_of_work:
            self._repository.save(order)
        return True
