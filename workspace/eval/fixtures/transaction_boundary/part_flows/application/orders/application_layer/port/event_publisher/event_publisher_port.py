from __future__ import annotations

from abc import ABC, abstractmethod

from application.orders.domain_layer.order.event.order_confirmed import OrderConfirmed


class EventPublisherPort(ABC):
    @abstractmethod
    def publish(self, event: OrderConfirmed) -> None: ...
