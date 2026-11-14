from __future__ import annotations

from application.orders.domain_layer.order.order import Order


class OrderLinkPolicy:
    """루트 메서드를 부른다(현장 꼴) — 꼴마다 메서드 하나."""

    @staticmethod
    def link(order: Order, lead: Order) -> None:
        if not lead.is_open():
            raise ValueError(lead.order_id)
        order.link_to(lead.order_id)

    @classmethod
    def link_by_class(cls, order: Order, lead: Order) -> None:
        order.link_to(lead.order_id)

    def link_with(self, order: Order, lead: Order) -> None:
        order.link_to(lead.order_id)

    @staticmethod
    def link_renamed(target: Order, lead: Order) -> None:
        target.link_to(lead.order_id)

    @staticmethod
    def link_alias(target: Order, lead: Order) -> None:
        alias = target
        alias.link_to(lead.order_id)
