from __future__ import annotations

from django.utils import timezone

from application.orders.domain_layer.payment.entity.receipt import Receipt
from application.orders.domain_layer.payment.value_object.currency import Currency
from application.orders.domain_layer.payment.refund_rule import RefundRule
from application.orders.domain_layer.payment.payment import Payment


class Order:
    lines: list

    def __init__(self, order_id: str) -> None:
        self.order_id: str = order_id
        self._events: list = []

    def attach(self, payment: Payment) -> None:
        self._payment: Payment = payment
        self._bus.publish(self._events[-1])

    def pull_events(self) -> list:
        return list(self._events)

    @property
    def events(self) -> list:
        return self._events
