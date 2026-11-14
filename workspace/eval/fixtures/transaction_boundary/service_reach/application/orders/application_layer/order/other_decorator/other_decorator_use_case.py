"""다른 데코레이터 메서드(위반)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.domain_service.order_rebind_policy import OrderRebindPolicy


class OtherDecoratorUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_id: int, lead_id: int) -> None:
        with self._unit_of_work:
            order: Order = self._repository.find_for_update(order_id)
            lead: Order = self._repository.find(lead_id)
            OrderRebindPolicy.link_cached(order, lead)
            self._repository.save_link(order)
