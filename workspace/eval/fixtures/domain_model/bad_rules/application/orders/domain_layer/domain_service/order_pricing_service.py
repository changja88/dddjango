from __future__ import annotations

from application.orders.domain_layer.order.entity.receipt import Receipt
from application.orders.domain_layer.order.order import Order

CACHE = {}


def apply_discount(order: Order) -> None:
    return None


def compute(rate: int, amount: int) -> int:
    return rate * amount


def can_refund(order: Order, marker: str) -> bool:
    return True


def settle(order: Order, repository: "OrderRepository") -> None:  # noqa: F821
    return None


def notify(order: Order, port: "EmailPort") -> None:  # noqa: F821
    return None


class PricingSession:
    def __init__(self) -> None:
        self.seen: dict = {}
