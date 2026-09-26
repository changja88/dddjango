"""#195 반복 원소 전파(F4-20) 이름 단위 fail-closed — 같은 함수에서 반복 변수 이름을 팩토리 컬렉션 루프와
조회 루프에 함께 쓰면 전파하지 않는다. 조회 루프의 필드 직접 대입 뒤 save(참양성)를 놓치지 않는 것이 목적이다
(팩토리 루프의 save 도 함께 red — fail-closed 대가)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class MixedOrdersUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_ids: list[str]) -> None:
        with self._unit_of_work:
            fresh: list[Order] = [Order.open_pending(order_id) for order_id in order_ids]
            order: Order
            for order in fresh:
                self._repository.save(order)
            for order in self._repository.list_open():
                order.status = "closed"
                self._repository.save(order)
