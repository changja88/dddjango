"""유스케이스가 값 객체를 읽음 · 서비스가 루트 메서드를 부름(통과)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.domain_service.plain_link_policy import PlainLinkPolicy


class LocalTermsReadUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_id: int, lead_id: int) -> None:
        with self._unit_of_work:
            order: Order = self._repository.find_for_update(order_id)
            lead: Order = self._repository.find(lead_id)
            PlainLinkPolicy.link(order=order, lead=lead)
            if not order.terms.allows_link():
                raise ValueError(lead_id)
            self._repository.save_link(order)
