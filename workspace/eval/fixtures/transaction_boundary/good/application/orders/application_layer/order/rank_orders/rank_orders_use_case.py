"""#195 반복 원소 전파(F4-20 · R8-D2) 순수 읽기 자리 — 가변 컬렉션(리스트 컴프리헨션)이라도 원소를 들이지
못하는 읽기(비교 `==` · 순서만 바꾸는 `reverse()`)만 받았으면 그 이름을 도는 반복 변수는 factory-born 이다."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class RankOrdersUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_ids: list[str]) -> None:
        with self._unit_of_work:
            orders: list[Order] = [Order.open_pending(order_id) for order_id in order_ids]
            if orders == []:
                return
            orders.reverse()
            order: Order
            for order in orders:
                self._repository.save(order)
