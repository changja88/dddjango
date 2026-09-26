"""#195 반복 원소 전파(F4-20) — 전량 생성 → 전량 검증 → 저장. 원소식이 팩토리 호출인
컬렉션(tuple(<genexpr>) · 리스트 컴프리헨션)을 도는 for 변수는 «x = <원소식>» 과 같게 factory-born 이다."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class ImportOrdersUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_ids: list[str]) -> None:
        with self._unit_of_work:
            orders: tuple[Order, ...] = tuple(Order.open_pending(order_id) for order_id in order_ids)
            order: Order
            for order in orders:
                self._repository.save(order)
