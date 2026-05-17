from __future__ import annotations

import json
from decimal import Decimal

from django.test import Client, TestCase

from apps.orders.models import Order
from apps.orders.services import IdempotencyConflict, order_create


class OrderCreateServiceTests(TestCase):
    def test_replays_same_idempotency_key_and_payload(self) -> None:
        first = order_create(
            idempotency_key="order-1",
            customer_email="BUYER@example.com",
            total_amount=Decimal("19.99"),
            note="gift",
        )
        second = order_create(
            idempotency_key="order-1",
            customer_email="buyer@example.com",
            total_amount=Decimal("19.99"),
            note="gift",
        )

        self.assertFalse(first.replayed)
        self.assertTrue(second.replayed)
        self.assertEqual(first.order.id, second.order.id)
        self.assertEqual(Order.objects.count(), 1)

    def test_rejects_idempotency_key_payload_conflict(self) -> None:
        order_create(
            idempotency_key="order-2",
            customer_email="buyer@example.com",
            total_amount=Decimal("19.99"),
        )

        with self.assertRaises(IdempotencyConflict):
            order_create(
                idempotency_key="order-2",
                customer_email="buyer@example.com",
                total_amount=Decimal("29.99"),
            )


class OrderCreateApiTests(TestCase):
    def test_order_endpoint_replays_same_request(self) -> None:
        client = Client()
        payload = {
            "customer_email": "buyer@example.com",
            "total_amount": "19.99",
            "note": "gift",
        }

        first = client.post(
            "/api/orders",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="api-order-1",
        )
        second = client.post(
            "/api/orders",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="api-order-1",
        )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json()["id"], second.json()["id"])
        self.assertFalse(first.json()["replayed"])
        self.assertTrue(second.json()["replayed"])

    def test_order_endpoint_rejects_conflicting_replay(self) -> None:
        client = Client()

        client.post(
            "/api/orders",
            data=json.dumps({"customer_email": "buyer@example.com", "total_amount": "19.99"}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="api-order-2",
        )
        conflict = client.post(
            "/api/orders",
            data=json.dumps({"customer_email": "buyer@example.com", "total_amount": "29.99"}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="api-order-2",
        )

        self.assertEqual(conflict.status_code, 409)
        self.assertIn("different payload", conflict.json()["detail"])
