"""틀 부품 — 저장 도구와 발행 도구를 쥔다. 발행 메서드는 본체가 커밋 뒤에 등록한다."""
from __future__ import annotations

from application.orders.application_layer.port.event_publisher.event_publisher_port import EventPublisherPort
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


class PayOrderFrame:
    def __init__(self, order_repository: OrderRepository, event_publisher: EventPublisherPort) -> None:
        self._order_repository: OrderRepository = order_repository
        self._event_publisher: EventPublisherPort = event_publisher

    def load_order(self, order_id: str) -> Order:
        return self._order_repository.get(order_id)

    def commit_order(self, order: Order) -> None:
        self._order_repository.save(order)

    def publish_paid(self) -> None:
        self._event_publisher.publish("paid")
