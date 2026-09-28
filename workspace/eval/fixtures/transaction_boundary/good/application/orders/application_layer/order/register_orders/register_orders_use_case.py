"""#195 반복 원소 전파(F4-20 · R8-D2) 불변 컬렉션 면제 — 원소식이 팩토리 호출인 tuple 컬렉션은 도메인
검증기 인자로 넘겨도 내용이 바뀌지 않으므로, 그 이름을 도는 반복 변수는 그대로 factory-born 이다."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class RegisterOrdersUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_ids: list[str]) -> None:
        with self._unit_of_work:
            orders: tuple[Order, ...] = tuple(Order.open_pending(order_id) for order_id in order_ids)
            Order.ensure_distinct_ids(orders)
            order: Order
            for order in orders:
                self._repository.save(order)
