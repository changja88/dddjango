"""#195 반복 원소 전파(F4-20) 이름 단위 fail-closed — 팩토리 컬렉션 이름을 조회 결과로 다시 대입하면
그 이름은 원소 출처를 물려주지 않는다(조회 원소의 필드 직접 대입 뒤 save 는 참양성)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class ReassignOrdersUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_ids: list[str]) -> None:
        with self._unit_of_work:
            orders: list[Order] = [Order.open_pending(order_id) for order_id in order_ids]
            orders = list(self._repository.list_open())
            for order in orders:
                order.status = "closed"
                self._repository.save(order)
