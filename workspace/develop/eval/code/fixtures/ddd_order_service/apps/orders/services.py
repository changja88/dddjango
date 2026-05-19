from __future__ import annotations

from apps.orders.models import Order, OrderStatus


_ORDERS: dict[str, Order] = {}


def place_order(customer_id: str, items: list[str]) -> Order:
    order = Order(customer_id=customer_id, items=items)
    if not items:
        raise ValueError("empty order")
    order.status = OrderStatus.PENDING_PAYMENT
    _ORDERS[order.id] = order
    return order


def confirm_order(order_id: str) -> Order:
    order = _ORDERS[order_id]
    order.status = OrderStatus.CONFIRMED
    return order
