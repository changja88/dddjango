from __future__ import annotations

from application.orders.domain_layer.order.event.order_placed import OrderPlaced
from application.orders.domain_layer.order.value_object.money import Money


class Order:
    def __init__(self, order_id: str) -> None:
        self.order_id: str = order_id
        self._events: list = []

    def place(self, total: Money) -> None:
        self._total: Money = total
        self._events.append(OrderPlaced(order_id=self.order_id))
        self._ensure_valid()

    def pull_events(self) -> list:
        drained: list = list(self._events)
        self._events.clear()
        return drained

    def _ensure_valid(self) -> None:
        return None
