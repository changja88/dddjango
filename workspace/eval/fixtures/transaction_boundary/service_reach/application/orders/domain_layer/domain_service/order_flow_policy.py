from __future__ import annotations

from application.orders.domain_layer.order.order import Order


class OrderFlowPolicy:
    """두 홉 — 같은 클래스 안 `cls._apply` · `self._apply`."""

    @classmethod
    def run(cls, order: Order, lead: Order) -> None:
        cls._apply(order, lead.order_id)

    def run_with(self, order: Order, lead: Order) -> None:
        self._apply(order, lead.order_id)

    @staticmethod
    def _apply(target: Order, lead_id: int) -> None:
        target.link_to(lead_id)
