"""bad_frame_publish_before_commit — 틀이 작업 단위 안에서 `.publish(` 를 직접 부른다(#541 · 본체 + 틀 넓힘)."""
from __future__ import annotations

from application.orders.application_layer.port.event_publisher.event_publisher_port import EventPublisherPort
from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class ShipParcelFrame:
    def __init__(self, order_repository: OrderRepository, unit_of_work: OrdersUnitOfWork,
                 event_publisher: EventPublisherPort) -> None:
        self._order_repository: OrderRepository = order_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work
        self._event_publisher: EventPublisherPort = event_publisher

    def load_order(self, order_id: str) -> Order:
        return self._order_repository.get(order_id)

    def save_shipped(self, order: Order) -> None:
        with self._unit_of_work:
            self._order_repository.save(order)
            self._event_publisher.publish(order.order_id)
