from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction

from .models import Order


class IdempotencyConflict(Exception):
    pass


@dataclass(frozen=True)
class OrderCreateResult:
    order: Order
    replayed: bool


def request_fingerprint(*, customer_email: str, total_amount: Decimal, note: str) -> str:
    payload = {
        "customer_email": customer_email.strip().lower(),
        "total_amount": str(total_amount),
        "note": note,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def order_create(
    *,
    idempotency_key: str,
    customer_email: str,
    total_amount: Decimal,
    note: str = "",
) -> OrderCreateResult:
    fingerprint = request_fingerprint(
        customer_email=customer_email,
        total_amount=total_amount,
        note=note,
    )
    with transaction.atomic():
        existing = (
            Order.objects.select_for_update()
            .filter(idempotency_key=idempotency_key)
            .first()
        )
        if existing is not None:
            if existing.request_fingerprint != fingerprint:
                raise IdempotencyConflict("idempotency key reused with a different payload")
            return OrderCreateResult(order=existing, replayed=True)

        order = Order.objects.create(
            customer_email=customer_email.strip().lower(),
            total_amount=total_amount,
            idempotency_key=idempotency_key,
            request_fingerprint=fingerprint,
            note=note,
        )
        return OrderCreateResult(order=order, replayed=False)
