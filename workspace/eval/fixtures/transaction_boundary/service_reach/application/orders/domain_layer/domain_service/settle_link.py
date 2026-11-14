from __future__ import annotations

from application.orders.domain_layer.order.order import Order


def settle_link(order: Order, lead: Order) -> None:
    _apply(order, lead.order_id)


def _apply(target: Order, lead_id: int) -> None:
    target.link_to(lead_id)
