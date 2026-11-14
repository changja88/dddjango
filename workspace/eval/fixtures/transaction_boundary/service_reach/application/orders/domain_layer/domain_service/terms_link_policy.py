from __future__ import annotations

from application.orders.domain_layer.order.order import Order


class TermsLinkPolicy:
    """값 객체를 읽고(`order.terms.allows_link()`) 루트 메서드를 부른다."""

    @staticmethod
    def link(order: Order, lead: Order) -> None:
        if not order.terms.allows_link():
            raise ValueError(lead.order_id)
        order.link_to(lead.order_id)
