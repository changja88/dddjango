"""#195 인자 받는 도메인 컬렉션 팩토리(R8-I2) 음성 경계 — 원소가 같은 클래스 메서드 호출(`cls.kept(order)`)이어도 그 메서드가 새로 짓는다고 증명되지 않으면
(받은 인스턴스를 그대로 돌려준다) 본문 증명이 서지 않는다
(조회 원소의 필드 직접 대입 뒤 save 는 참양성)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class RetouchOrdersUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self) -> None:
        with self._unit_of_work:
            for order in Order.retouched(self._repository.list_open()):
                order.status = "closed"
                self._repository.save(order)
