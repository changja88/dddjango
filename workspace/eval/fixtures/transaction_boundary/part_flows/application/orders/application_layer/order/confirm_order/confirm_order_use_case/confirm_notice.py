from __future__ import annotations

from application.orders.application_layer.port.event_publisher.event_publisher_port import EventPublisherPort
from application.orders.domain_layer.order.event.order_confirmed import OrderConfirmed

from .confirm_order_frame import ConfirmOrderFrame


class ConfirmNotice:
    def __init__(self, frame: ConfirmOrderFrame, event_publisher: EventPublisherPort) -> None:
        self._frame: ConfirmOrderFrame = frame
        self._event_publisher: EventPublisherPort = event_publisher

    def run(self, order_id: str) -> bool:
        if not self._frame.commit_order_change(order_id, lambda current: current.confirm()):
            return False
        self._event_publisher.publish(OrderConfirmed(order_id=order_id))
        return True
