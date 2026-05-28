"""Acceptance (outer-loop / blackbox) concurrency test for POST /api/v1/orders.

Single source of truth: .dddjango/order-create-with-stock/design-spec.md (sections 3.2, 3.3, 6.6)

Covered observable behavior:
- B6: concurrent requests never oversell. With N concurrent orders against
  limited stock, the sum of deductions never exceeds the initial stock,
  stock never goes negative, and the number of 201s equals
  (deducted stock / quantity per order).

Per spec section 3.3, SQLite writer-lock contention ("database is locked")
is a separate concern from correctness (oversell). This test absorbs lock
contention via a busy_timeout PRAGMA and bounded retry so the assertions
verify OVERSELL behavior, not lock exceptions. Correctness itself is
guaranteed by the conditional atomic UPDATE in the implementation, which
does not yet exist -- so this test is Red (no endpoint / always rejects).
"""

import json
import threading

import pytest
from django.db import connection
from django.test import Client

from catalog.models import Product

ENDPOINT = "/api/v1/orders"


def _enable_busy_timeout():
    """Mitigate SQLite writer-lock contention so the test measures oversell,
    not 'database is locked'. (spec section 3.3 -- test-env lock handling.)"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA busy_timeout = 5000;")
    except Exception:
        pass


def _post_order(product_id, quantity, results, index):
    client = Client()
    body = json.dumps({"product_id": product_id, "quantity": quantity})

    last_status = None
    # Bounded retry only for SQLite lock contention (NOT for oversell).
    for _ in range(10):
        _enable_busy_timeout()
        try:
            response = client.post(
                ENDPOINT, data=body, content_type="application/json"
            )
        except Exception as exc:  # pragma: no cover - lock contention path
            if "database is locked" in str(exc).lower():
                continue
            raise
        last_status = response.status_code
        break

    results[index] = last_status


@pytest.mark.django_db(transaction=True)
def test_concurrent_orders_do_not_oversell():
    initial_stock = 10
    quantity_per_order = 1
    concurrent_requests = 30  # far more than stock -> forces contention
    product = Product.objects.create(
        name="Limited", price=1000, stock=initial_stock
    )

    results = [None] * concurrent_requests
    threads = [
        threading.Thread(
            target=_post_order,
            args=(product.id, quantity_per_order, results, i),
        )
        for i in range(concurrent_requests)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    product.refresh_from_db()
    successes = sum(1 for status in results if status == 201)

    # Oversell prevention: stock never negative.
    assert product.stock >= 0
    # Exactly initial_stock units sold, no more, no less.
    assert successes == initial_stock // quantity_per_order
    # Deducted amount matches successful orders -- no phantom deductions.
    assert product.stock == initial_stock - successes * quantity_per_order


@pytest.mark.django_db(transaction=True)
def test_concurrent_orders_multi_unit_do_not_oversell():
    """Same invariant with quantity > 1: total deducted never exceeds stock."""
    initial_stock = 10
    quantity_per_order = 3
    concurrent_requests = 20
    product = Product.objects.create(
        name="Limited", price=1000, stock=initial_stock
    )

    results = [None] * concurrent_requests
    threads = [
        threading.Thread(
            target=_post_order,
            args=(product.id, quantity_per_order, results, i),
        )
        for i in range(concurrent_requests)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    product.refresh_from_db()
    successes = sum(1 for status in results if status == 201)

    assert product.stock >= 0
    assert successes == initial_stock // quantity_per_order  # 3 orders -> 9 units
    assert product.stock == initial_stock - successes * quantity_per_order
