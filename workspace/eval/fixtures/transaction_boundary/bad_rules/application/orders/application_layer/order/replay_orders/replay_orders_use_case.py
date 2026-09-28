"""#195 도메인 컬렉션 팩토리(R8-D2) 출처 가드 — 도메인 밖(driven)에서 들여온 동명 클래스의 무인자 컬렉션
호출은 조회를 돌려줄 수 있어 원소를 factory-born 으로 보지 않는다(필드 직접 대입 뒤 save 는 참양성)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.driven_layer.persistence.order_record import Order


class ReplayOrdersUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self) -> None:
        with self._unit_of_work:
            for order in Order.open_rows():
                order.status = "closed"
                self._repository.save(order)
