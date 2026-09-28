"""#195 도메인 컬렉션 팩토리(R8-D2) — 인자 없는 도메인 classmethod 가 자기 타입 컬렉션을 돌려준다고
선언하면(`tuple["Order", ...]`) 그 호출을 도는 반복 변수·그 호출에 묶인 컬렉션 이름은 factory-born 이다."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class SeedOrdersUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, requested_by: str) -> None:
        with self._unit_of_work:
            order: Order
            for order in Order.seed_batch():
                self._repository.save(order)
            batch: tuple[Order, ...] = Order.seed_batch()
            seeded: Order
            for seeded in batch:
                self._repository.save(seeded)
