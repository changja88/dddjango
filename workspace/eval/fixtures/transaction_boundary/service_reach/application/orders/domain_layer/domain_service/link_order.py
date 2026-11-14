from __future__ import annotations

from application.orders.domain_layer.order.order import Order


def link_order(order: Order, lead: Order) -> None:
    order.link_to(lead.order_id)
