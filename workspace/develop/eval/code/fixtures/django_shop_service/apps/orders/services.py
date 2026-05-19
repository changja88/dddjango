from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction

from .models import Order


@dataclass(frozen=True)
class OrderCreateResult:
    order: Order
    replayed: bool


def order_create(
    *,
    idempotency_key: str,
    customer_email: str,
    total_amount: Decimal,
    note: str = "",
) -> OrderCreateResult:
    with transaction.atomic():
        order = Order.objects.create(
            customer_email=customer_email.strip().lower(),
            total_amount=total_amount,
            idempotency_key=idempotency_key.strip(),
            request_fingerprint="",
            note=note,
        )
        return OrderCreateResult(order=order, replayed=False)
