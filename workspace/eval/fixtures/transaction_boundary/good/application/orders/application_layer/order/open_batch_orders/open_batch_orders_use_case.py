"""#195 인자 받는 도메인 컬렉션 팩토리(R8-I2) — 본문이 원소를 모두 새로 짓는다고 보이면(같은 클래스 단일 팩토리
`cls.open_pending(..)` 만 append 한 지역 리스트의 tuple 복사) 인자를 받아도 그 호출을 도는 반복 변수는 factory-born 이다."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class OpenBatchOrdersUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_ids: tuple[str, ...]) -> None:
        with self._unit_of_work:
            order: Order
            for order in Order.open_batch(order_ids):
                self._repository.save(order)
