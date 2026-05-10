from __future__ import annotations

from apps.orders.models import Order, OrderStatus


_ORDERS: dict[str, Order] = {}


def create_order(customer_id: str, items: list[str], memo: str = "") -> Order:
    order = Order(customer_id=customer_id, items=items, memo=memo)
    order.status = OrderStatus.PENDING
    _ORDERS[order.id] = order
    return order


def confirm_order(order_id: str) -> Order:
    order = _ORDERS[order_id]
    order.confirm()
    send_confirmation_email(order)
    return order


def send_confirmation_email(order: Order) -> None:
    # Side effect placeholder for eval cases.
    return None
