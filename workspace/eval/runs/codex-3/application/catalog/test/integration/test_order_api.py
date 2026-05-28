import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from django.db import connection
from django.test import Client, TransactionTestCase


class OrderApiAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def test_existing_product_with_sufficient_stock_creates_order_and_decrements_stock(self):
        """Behavior: valid order returns 201, creates an order, and decrements stock."""
        product_id = self.create_product(price=1500, stock=5)

        response = self.post_json("/api/orders/", {"product_id": product_id, "quantity": 2})

        self.assertEqual(response.status_code, 201)
        self.assert_json_response(response)
        body = response.json()
        self.assertIsInstance(body["id"], int)
        self.assertEqual(body["product_id"], product_id)
        self.assertEqual(body["quantity"], 2)
        self.assertEqual(body["unit_price"], 1500)
        self.assertIn("created_at", body)
        self.assertEqual(self.product_stock(product_id), 3)
        self.assertEqual(self.order_count(), 1)
        self.assertEqual(
            self.order_rows(),
            [{"product_id": product_id, "quantity": 2, "unit_price": 1500}],
        )

    def test_existing_product_with_insufficient_stock_returns_409_without_changes(self):
        """Behavior: insufficient stock returns 409, creates no order, and preserves stock."""
        product_id = self.create_product(price=2500, stock=1)

        response = self.post_json("/api/orders/", {"product_id": product_id, "quantity": 2})

        self.assert_problem(
            response,
            status=409,
            problem_type="urn:problem:catalog:insufficient-stock",
            title="Insufficient stock",
        )
        self.assertEqual(self.product_stock(product_id), 1)
        self.assertEqual(self.order_count(), 0)

    def test_unknown_product_returns_404_without_creating_order(self):
        """Behavior: unknown product returns 404 and creates no order."""
        response = self.post_json("/api/orders/", {"product_id": 999_999, "quantity": 1})

        self.assert_problem(
            response,
            status=404,
            problem_type="urn:problem:catalog:product-not-found",
            title="Product not found",
        )
        self.assertEqual(self.order_count(), 0)

    def test_invalid_order_requests_return_400_problem_details(self):
        """Behavior: invalid shapes, non-positive values, and unknown fields return 400."""
        cases = [
            ({"product_id": 1}, "quantity"),
            ({"product_id": 1, "quantity": 0}, "quantity"),
            ({"product_id": 1, "quantity": 1, "coupon_code": "SUMMER"}, "coupon_code"),
            ({"product_id": "abc", "quantity": 1}, "product_id"),
        ]

        for payload, expected_error_field in cases:
            with self.subTest(payload=payload):
                response = self.post_json("/api/orders/", payload)

                body = self.assert_problem(
                    response,
                    status=400,
                    problem_type="urn:problem:catalog:invalid-order-request",
                    title="Invalid order request",
                )
                self.assertIn("errors", body)
                self.assertIn(expected_error_field, body["errors"])
                self.assertNotIn("instance", body)

    def test_non_json_request_content_returns_415_problem_details(self):
        """Behavior: unsupported request content type returns 415 Problem Details."""
        response = Client().post(
            "/api/orders/",
            data="product_id=1&quantity=1",
            content_type="application/x-www-form-urlencoded",
            HTTP_ACCEPT="application/json",
        )

        self.assert_problem(
            response,
            status=415,
            problem_type="urn:problem:catalog:unsupported-media-type",
            title="Unsupported media type",
        )

    def test_competing_order_attempts_do_not_reduce_stock_below_zero(self):
        """Behavior: competing attempts can only create orders covered by available stock."""
        product_id = self.create_product(price=900, stock=1)
        barrier = Barrier(2)

        def place_order():
            barrier.wait(timeout=5)
            client = Client()
            response = client.post(
                "/api/orders/",
                data=json.dumps({"product_id": product_id, "quantity": 1}),
                content_type="application/json",
                HTTP_ACCEPT="application/json",
            )
            return response.status_code

        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = sorted(executor.map(lambda _: place_order(), range(2)))

        self.assertEqual(statuses, [201, 409])
        self.assertEqual(self.product_stock(product_id), 0)
        self.assertEqual(self.order_count(), 1)

    def create_product(self, *, price, stock):
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO catalog_product (name, price, stock) VALUES (%s, %s, %s)",
                ["Acceptance test product", price, stock],
            )
            return cursor.lastrowid

    def product_stock(self, product_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT stock FROM catalog_product WHERE id = %s", [product_id])
            row = cursor.fetchone()
        self.assertIsNotNone(row)
        return row[0]

    def order_count(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM catalog_order")
            row = cursor.fetchone()
        return row[0]

    def order_rows(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT product_id, quantity, unit_price FROM catalog_order ORDER BY id"
            )
            rows = cursor.fetchall()
        return [
            {"product_id": product_id, "quantity": quantity, "unit_price": unit_price}
            for product_id, quantity, unit_price in rows
        ]

    def post_json(self, path, payload):
        return Client().post(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_ACCEPT="application/json",
        )

    def assert_json_response(self, response):
        content_type = response["Content-Type"].split(";")[0]
        self.assertEqual(content_type, "application/json")

    def assert_problem(self, response, *, status, problem_type, title):
        self.assertEqual(response.status_code, status)
        content_type = response["Content-Type"].split(";")[0]
        self.assertEqual(content_type, "application/problem+json")
        body = response.json()
        self.assertEqual(body["type"], problem_type)
        self.assertEqual(body["title"], title)
        self.assertEqual(body["status"], status)
        self.assertIsInstance(body["detail"], str)
        self.assertTrue(body["detail"])
        return body
