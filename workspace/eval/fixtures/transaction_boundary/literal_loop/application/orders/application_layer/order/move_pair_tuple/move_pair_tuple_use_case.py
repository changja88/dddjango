"""#195 0 줄 — 싸지 않은 글자 튜플도 같다(원소가 모두 루트 메서드 호출을 받음 · 이체 꼴 판정은 check-domain-model 몫)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class MovePairTupleUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            source: Order = self._repository.get(order_id)
            target: Order = self._repository.get(other_id)
            source.cancel()
            target.move_to(source.order_id)
            for order in (source, target):
                self._repository.save(order)
