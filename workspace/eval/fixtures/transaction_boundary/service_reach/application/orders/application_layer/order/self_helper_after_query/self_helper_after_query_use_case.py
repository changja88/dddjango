"""조회 서비스 뒤 유스케이스가 `self._` 도우미에 넘겨 칸을 바꿈(위반)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.domain_service.order_query_policy import OrderQueryPolicy


class SelfHelperAfterQueryUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def _stamp_lead(self, target: Order, lead_id: int) -> None:
        target.lead_id = lead_id

    def execute(self, order_id: int, lead_id: int) -> None:
        with self._unit_of_work:
            order: Order = self._repository.find_for_update(order_id)
            lead: Order = self._repository.find(lead_id)
            OrderQueryPolicy.ensure(order=order, lead=lead)
            self._stamp_lead(order, lead_id)
            self._repository.save_link(order)
