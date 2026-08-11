from __future__ import annotations

from application.orders.domain_layer.order.order_repository import OrderRepository


class DjangoOrderRepository(OrderRepository):
    def save(self, order: object) -> None:
        if order._events:
            raise PendingEventsGuard()  # noqa: F821
        return None
