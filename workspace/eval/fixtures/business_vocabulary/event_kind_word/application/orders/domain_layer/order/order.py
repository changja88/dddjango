from __future__ import annotations

from application.orders.domain_layer.order.event.order_placed import OrderPlacedEvent


class Order:
    def __init__(self, order_id: str) -> None:
        self.order_id: str = order_id
        self._events: list = []

    def place(self, sku: str) -> None:
        self._sku: str = sku
        self._events.append(OrderPlacedEvent(order_id=self.order_id))
        self._ensure_valid()

    def pull_events(self) -> list:
        drained: list = list(self._events)
        self._events.clear()
        return drained

    def _ensure_valid(self) -> None:
        return None
