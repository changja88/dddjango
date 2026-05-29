import json
import threading
from unittest.mock import patch

from django.apps import apps
from django.test import Client, TestCase, TransactionTestCase

from catalog.models import Product
from application.orders.domain_layer.order.port.product_inventory_port import (
    InventoryConflict,
    ProductInventorySnapshot,
)


class OrderModelLookupMixin:
    def _order_model(self):
        return apps.get_model("orders", "OrderModel")


class CreateOrderApiAcceptanceTests(OrderModelLookupMixin, TestCase):
    endpoint = "/api/orders/"

    def test_sufficient_stock_creates_order_and_decrements_stock(self):
        product = Product.objects.create(name="Keyboard", price=10000, stock=5)
        initial_version = product.version

        response = self.client.post(
            self.endpoint,
            data={"product_id": product.id, "quantity": 2},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response["Content-Type"], "application/json")
        body = response.json()
        self.assertIsInstance(body["id"], int)
        self.assertEqual(body["product_id"], product.id)
        self.assertEqual(body["quantity"], 2)
        self.assertEqual(body["status"], "created")

        product.refresh_from_db()
        self.assertEqual(product.stock, 3)
        self.assertEqual(product.version, initial_version + 1)
        order_model = self._order_model()
        self.assertEqual(order_model.objects.count(), 1)
        order = order_model.objects.get()
        self.assertEqual(order.product_id, product.id)
        self.assertEqual(order.quantity, 2)
        self.assertEqual(order.status, "created")

    def test_insufficient_stock_returns_409_and_leaves_state_unchanged(self):
        product = Product.objects.create(name="Mouse", price=3000, stock=1)

        response = self.client.post(
            self.endpoint,
            data={"product_id": product.id, "quantity": 2},
            content_type="application/json",
        )

        self.assertProblem(
            response,
            status=409,
            type_="/problems/insufficient-stock",
            title="Insufficient stock",
        )
        body = response.json()
        self.assertEqual(body["available_stock"], 1)
        self.assertEqual(body["requested_quantity"], 2)
        product.refresh_from_db()
        self.assertEqual(product.stock, 1)
        self.assertEqual(self._order_model().objects.count(), 0)

    def test_missing_or_non_json_content_type_returns_415_and_creates_no_order(self):
        product = Product.objects.create(name="Monitor", price=20000, stock=5)
        cases = [
            ("missing", ""),
            ("non_json", "text/plain"),
        ]

        for case_name, content_type in cases:
            with self.subTest(case_name=case_name):
                response = self.client.post(
                    self.endpoint,
                    data=json.dumps({"product_id": product.id, "quantity": 1}),
                    content_type=content_type,
                )

                self.assertProblem(
                    response,
                    status=415,
                    type_="/problems/unsupported-media-type",
                    title="Unsupported Media Type",
                )
                product.refresh_from_db()
                self.assertEqual(product.stock, 5)
                self.assertEqual(self._order_model().objects.count(), 0)

    def test_invalid_request_bodies_return_400_and_create_no_order(self):
        product = Product.objects.create(name="Cable", price=1000, stock=5)
        invalid_cases = [
            ("malformed_json", '{"product_id": 1, "quantity":'),
            ("missing_product_id", {"quantity": 1}),
            ("missing_quantity", {"product_id": product.id}),
            ("non_integer_product_id", {"product_id": "abc", "quantity": 1}),
            ("non_integer_quantity", {"product_id": product.id, "quantity": "two"}),
            ("non_positive_product_id", {"product_id": 0, "quantity": 1}),
            ("non_positive_quantity", {"product_id": product.id, "quantity": 0}),
        ]

        for case_name, payload in invalid_cases:
            with self.subTest(case_name=case_name):
                response = self.client.post(
                    self.endpoint,
                    data=payload,
                    content_type="application/json",
                )

                self.assertProblem(
                    response,
                    status=400,
                    type_="/problems/invalid-order-request",
                    title="Invalid order request",
                )
                product.refresh_from_db()
                self.assertEqual(product.stock, 5)
                self.assertEqual(self._order_model().objects.count(), 0)

    def test_unknown_product_returns_404_and_creates_no_order(self):
        response = self.client.post(
            self.endpoint,
            data={"product_id": 999999, "quantity": 1},
            content_type="application/json",
        )

        self.assertProblem(
            response,
            status=404,
            type_="/problems/product-not-found",
            title="Product not found",
        )
        self.assertEqual(self._order_model().objects.count(), 0)

    def test_unresolved_inventory_conflict_returns_409_problem(self):
        with patch(
            "application.orders.presentation_layer.api.create_order.api_orders."
            "DjangoProductInventoryPort",
            return_value=AlwaysConflictingProductInventoryPort(),
        ):
            response = self.client.post(
                self.endpoint,
                data={"product_id": 77, "quantity": 2},
                content_type="application/json",
            )

        self.assertProblem(
            response,
            status=409,
            type_="/problems/inventory-conflict",
            title="Inventory conflict",
        )
        self.assertEqual(self._order_model().objects.count(), 0)

    def assertProblem(self, response, *, status, type_, title):
        self.assertEqual(response.status_code, status)
        self.assertEqual(response["Content-Type"], "application/problem+json")
        body = response.json()
        self.assertEqual(body["type"], type_)
        self.assertEqual(body["title"], title)
        self.assertEqual(body["status"], status)
        self.assertIsInstance(body["detail"], str)
        self.assertTrue(body["detail"])


class AlwaysConflictingProductInventoryPort:
    def __init__(self) -> None:
        self.snapshots = [
            ProductInventorySnapshot(product_id=77, available_stock=5, version=1),
            ProductInventorySnapshot(product_id=77, available_stock=5, version=2),
        ]

    def load_snapshot(self, product_id):
        return self.snapshots.pop(0)

    def decrement_stock(self, snapshot, quantity) -> None:
        raise InventoryConflict("stale inventory")


class CreateOrderConcurrencyAcceptanceTests(OrderModelLookupMixin, TransactionTestCase):
    endpoint = "/api/orders/"

    def test_concurrent_orders_do_not_oversell_inventory(self):
        product = Product.objects.create(name="Desk", price=50000, stock=2)
        barrier = threading.Barrier(2)
        responses = []
        errors = []

        def post_order():
            client = Client()
            try:
                barrier.wait(timeout=5)
                response = client.post(
                    self.endpoint,
                    data={"product_id": product.id, "quantity": 2},
                    content_type="application/json",
                )
            except Exception as exc:
                errors.append(exc)
            else:
                responses.append(response)

        threads = [threading.Thread(target=post_order) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=5)

        self.assertEqual(errors, [])
        self.assertEqual(len(responses), 2)
        successes = [response for response in responses if response.status_code == 201]
        conflicts = [response for response in responses if response.status_code == 409]
        self.assertEqual(len(successes), 1)
        self.assertEqual(len(conflicts), 1)
        conflict_body = conflicts[0].json()
        self.assertIn(
            conflict_body["type"],
            ["/problems/insufficient-stock", "/problems/inventory-conflict"],
        )

        product.refresh_from_db()
        self.assertEqual(product.stock, 0)
        self.assertEqual(self._order_model().objects.count(), 1)
