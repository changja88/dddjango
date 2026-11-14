from __future__ import annotations

from application.orders.domain_layer.order.order import Order


class OrderFieldPolicy:
    """루트 메서드를 건너뛰고 칸에 직접 대입한다."""

    @staticmethod
    def link(order: Order, lead: Order) -> None:
        order.lead_id = lead.order_id

    @staticmethod
    def link_and_patch(order: Order, lead: Order) -> None:
        order.link_to(lead.order_id)
        order.label = "linked"
