"""#195 인자 받는 도메인 컬렉션 팩토리(R8-I2) 음성 경계 — 새로 지은 원소로 시작한 누적 리스트라도 받은 컬렉션을 `extend` 로 들이면 본문 증명이 서지 않는다
(조회 원소의 필드 직접 대입 뒤 save 는 참양성)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class MergeOrdersUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self) -> None:
        with self._unit_of_work:
            for order in Order.merged_with(self._repository.list_open()):
                order.status = "closed"
                self._repository.save(order)
