from __future__ import annotations

from application.orders.domain_layer.order.order import Order


class OrderLeadPolicy:
    """루트 메서드를 다른 인자(lead)에만 부른다."""

    @staticmethod
    def link(order: Order, lead: Order) -> None:
        if order.label:
            lead.link_to(order.order_id)
