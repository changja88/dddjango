"""#195 그대로 — 글자 고리 원소 하나(`target`)가 루트 메서드 호출을 받지 않았다."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class MovePairOneUntouchedUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            source: Order = self._repository.get(order_id)
            target: Order = self._repository.get(other_id)
            source.cancel()
            order: Order
            for order in sorted((source, target), key=lambda item: item.order_id):
                if not self._repository.save_with_version_guard(order):
                    raise RuntimeError(order.order_id)
