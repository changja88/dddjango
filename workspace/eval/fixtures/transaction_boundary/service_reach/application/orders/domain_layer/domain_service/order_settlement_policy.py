from __future__ import annotations

from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.domain_service.order_link_policy import OrderLinkPolicy


class OrderSettlementPolicy:
    """두 홉 — 형제 도메인 서비스로 넘긴다."""

    @staticmethod
    def settle(order: Order, lead: Order) -> None:
        OrderLinkPolicy.link(order=order, lead=lead)
