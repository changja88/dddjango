from __future__ import annotations

import functools

from application.orders.domain_layer.order.order import Order


class OrderRebindPolicy:
    """파라미터를 다시 묶은 뒤 부른다 · 다른 데코레이터."""

    @staticmethod
    def link(order: Order, lead: Order) -> None:
        order = lead
        order.link_to(lead.order_id)

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def link_cached(order: Order, lead: Order) -> None:
        order.link_to(lead.order_id)
