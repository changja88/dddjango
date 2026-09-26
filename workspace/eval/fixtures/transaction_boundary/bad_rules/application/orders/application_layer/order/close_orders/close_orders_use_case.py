"""#195 반복 원소 전파(F4-20) 음성 경계 — 조회 컬렉션을 list(...) 로 감싸도 원소는 팩토리 출생이 아니다."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository


class CloseOrdersUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self) -> None:
        with self._unit_of_work:
            orders = list(self._repository.list_open())
            for order in orders:
                order.status = "closed"
                self._repository.save(order)
