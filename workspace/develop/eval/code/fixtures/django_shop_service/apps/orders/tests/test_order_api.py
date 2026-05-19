from __future__ import annotations

import json
from decimal import Decimal

from django.test import Client, TestCase

from apps.orders.models import Order
from apps.orders.services import order_create


class OrderCreateServiceTests(TestCase):
    def test_creates_order(self) -> None:
        result = order_create(
            idempotency_key="order-1",
            customer_email="BUYER@example.com",
            total_amount=Decimal("19.99"),
            note="gift",
        )

        self.assertFalse(result.replayed)
        self.assertEqual(result.order.customer_email, "buyer@example.com")
        self.assertEqual(Order.objects.count(), 1)


class OrderCreateApiTests(TestCase):
    def test_order_endpoint_creates_order(self) -> None:
        client = Client()
        payload = {
            "customer_email": "buyer@example.com",
            "total_amount": "19.99",
            "note": "gift",
        }

        response = client.post(
            "/api/orders",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="api-order-1",
        )

        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.json()["replayed"])
        self.assertEqual(response.json()["customer_email"], "buyer@example.com")
