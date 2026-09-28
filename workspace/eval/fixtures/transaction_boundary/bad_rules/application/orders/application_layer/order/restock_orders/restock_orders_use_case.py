"""#195 도메인 컬렉션 팩토리(R8-D2) 이름 단위 fail-closed — 인자 없는 도메인 컬렉션 팩토리로 지은 컬렉션이라도
그 이름이 반복 원천 밖으로 새면(`extend` 로 조회 결과를 섞는다) 원소 출처를 물려주지 않는다
(조회 원소의 필드 직접 대입 뒤 save 는 참양성)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class RestockOrdersUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self) -> None:
        with self._unit_of_work:
            orders: list[Order] = list(Order.seed_batch())
            orders.extend(self._repository.list_open())
            order: Order
            for order in orders:
                order.status = "closed"
                self._repository.save(order)
