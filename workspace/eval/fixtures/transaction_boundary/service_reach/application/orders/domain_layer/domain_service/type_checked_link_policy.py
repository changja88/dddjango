from __future__ import annotations

from application.orders.domain_layer.order.order import Order


class TypeCheckedLinkPolicy:
    """읽기 전용 내장(`isinstance`)에 넘긴 뒤 루트 메서드를 부른다."""

    @staticmethod
    def link(order: Order, lead: Order) -> None:
        if not isinstance(order, Order):
            raise TypeError(lead.order_id)
        order.link_to(lead.order_id)
