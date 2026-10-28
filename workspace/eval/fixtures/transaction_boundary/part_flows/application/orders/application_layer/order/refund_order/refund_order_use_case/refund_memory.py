from __future__ import annotations

from dataclasses import dataclass

from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository


@dataclass(frozen=True)
class RefundMemory:
    order_id: str
    was_open: bool


def load_refund_memory(repository: OrderRepository, order_id: str) -> RefundMemory:
    order: Order = repository.get(order_id)
    return RefundMemory(order_id=order_id, was_open=order.is_open())
