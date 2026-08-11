from __future__ import annotations

from application.orders.domain_layer.order.order import Order


def order_precedence(first: Order, second: Order) -> Order:
    return first
