from __future__ import annotations

from collections.abc import Callable

from application.orders.domain_layer.order.order import Order


def _traced(fn: Callable[..., None]) -> Callable[..., None]:
    return fn


@_traced
def link_order_traced(order: Order, lead: Order) -> None:
    order.link_to(lead.order_id)
