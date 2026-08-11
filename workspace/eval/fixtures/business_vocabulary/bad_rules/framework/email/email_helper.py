from __future__ import annotations

from application.orders.domain_layer.order.order import Order


def choose_route(weight: int) -> str:
    if weight > 100:
        return "bulk"
    return "plain"
