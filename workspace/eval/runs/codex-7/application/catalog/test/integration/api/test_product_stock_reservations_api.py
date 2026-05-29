import json
import threading
from typing import Any

from django.db import close_old_connections
from django.http import HttpResponse
from django.test import Client, TestCase, TransactionTestCase

from catalog.models import Product
from application.catalog.catalog_api_router import catalog_api


def reservation_url(product_id: int) -> str:
    return f"/api/catalog/products/{product_id}/stock-reservations"


def problem_body(response: HttpResponse) -> dict[str, Any]:
    return response.json()


class ProductStockReservationApiTests(TestCase):
    def test_openapi_request_body_exposes_quantity_schema(self) -> None:
        schema = catalog_api.get_openapi_schema()
        operation = schema["paths"][
            "/api/catalog/products/{product_id}/stock-reservations"
        ]["post"]

        self.assertIn("requestBody", operation)
        request_body = operation["requestBody"]
        body_schema = request_body["content"]["application/json"]["schema"]
        if "$ref" in body_schema:
            schema_ref = body_schema["$ref"].removeprefix("#/components/schemas/")
            body_schema = schema["components"]["schemas"][schema_ref]
        quantity_schema = body_schema["properties"]["quantity"]

        self.assertTrue(request_body["required"])
        self.assertEqual(quantity_schema["type"], "integer")
        self.assertEqual(quantity_schema["minimum"], 1)

    def test_reserving_available_stock_decrements_stock_and_returns_remaining_stock(self):
        product = Product.objects.create(name="Widget", price=1000, stock=10)

        response = self.client.post(
            reservation_url(product.id),
            data={"quantity": 3},
            content_type="application/json",
        )

        product.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertNotIn("Location", response)
        self.assertNotIn("Retry-After", response)
        self.assertEqual(problem_body(response), {"product_id": product.id, "stock": 7})
        self.assertEqual(product.stock, 7)

    def test_reserving_exactly_available_stock_succeeds_and_leaves_zero_stock(self):
        product = Product.objects.create(name="Widget", price=1000, stock=3)

        response = self.client.post(
            reservation_url(product.id),
            data={"quantity": 3},
            content_type="application/json",
        )

        product.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(problem_body(response), {"product_id": product.id, "stock": 0})
        self.assertEqual(product.stock, 0)

    def test_insufficient_stock_returns_problem_details_and_does_not_change_stock(self):
        product = Product.objects.create(name="Widget", price=1000, stock=2)

        response = self.client.post(
            reservation_url(product.id),
            data={"quantity": 3},
            content_type="application/json",
        )

        product.refresh_from_db()
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response["Content-Type"], "application/problem+json")
        self.assertEqual(
            problem_body(response),
            {
                "type": "/problems/insufficient-product-stock",
                "title": "Insufficient product stock",
                "status": 409,
                "detail": (
                    f"Product {product.id} has insufficient stock for the requested quantity."
                ),
                "instance": reservation_url(product.id),
                "product_id": product.id,
                "requested_quantity": 3,
                "available_stock": 2,
            },
        )
        self.assertEqual(product.stock, 2)

    def test_missing_product_returns_not_found_problem_details(self):
        missing_product_id = 999

        response = self.client.post(
            reservation_url(missing_product_id),
            data={"quantity": 1},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["Content-Type"], "application/problem+json")
        self.assertEqual(
            problem_body(response),
            {
                "type": "/problems/product-not-found",
                "title": "Product not found",
                "status": 404,
                "detail": f"Product {missing_product_id} was not found.",
                "instance": reservation_url(missing_product_id),
                "product_id": missing_product_id,
            },
        )

    def test_invalid_quantity_returns_bad_request_problem_details(self):
        product = Product.objects.create(name="Widget", price=1000, stock=10)
        invalid_payloads = [
            {},
            {"quantity": "3"},
            {"quantity": 0},
            {"quantity": -1},
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post(
                    reservation_url(product.id),
                    data=payload,
                    content_type="application/json",
                )

                self.assertEqual(response.status_code, 400)
                self.assertEqual(response["Content-Type"], "application/problem+json")
                body = problem_body(response)
                self.assertEqual(body["type"], "/problems/invalid-reservation-request")
                self.assertEqual(body["title"], "Invalid reservation request")
                self.assertEqual(body["status"], 400)
                self.assertEqual(body["instance"], reservation_url(product.id))
                self.assertIsInstance(body["detail"], str)
                self.assertGreater(len(body["detail"]), 0)
                self.assertIsInstance(body["errors"], list)
                self.assertGreater(len(body["errors"]), 0)

    def test_malformed_json_returns_bad_request_problem_details(self):
        product = Product.objects.create(name="Widget", price=1000, stock=10)

        response = self.client.post(
            reservation_url(product.id),
            data='{"quantity":',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response["Content-Type"], "application/problem+json")
        body = problem_body(response)
        self.assertEqual(body["type"], "/problems/invalid-reservation-request")
        self.assertEqual(body["title"], "Invalid reservation request")
        self.assertEqual(body["status"], 400)
        self.assertEqual(body["instance"], reservation_url(product.id))
        self.assertIsInstance(body["detail"], str)
        self.assertGreater(len(body["detail"]), 0)
        self.assertIsInstance(body["errors"], list)
        self.assertGreater(len(body["errors"]), 0)

    def test_non_json_request_body_returns_unsupported_media_type_problem_details(self):
        product = Product.objects.create(name="Widget", price=1000, stock=10)

        response = self.client.post(
            reservation_url(product.id),
            data="quantity=1",
            content_type="application/x-www-form-urlencoded",
        )

        self.assertEqual(response.status_code, 415)
        self.assertEqual(response["Content-Type"], "application/problem+json")
        self.assertEqual(
            problem_body(response),
            {
                "type": "/problems/unsupported-media-type",
                "title": "Unsupported media type",
                "status": 415,
                "detail": "Content-Type must be application/json.",
                "instance": reservation_url(product.id),
            },
        )

    def test_repeating_successful_post_decrements_stock_again(self):
        product = Product.objects.create(name="Widget", price=1000, stock=10)

        first_response = self.client.post(
            reservation_url(product.id),
            data={"quantity": 2},
            content_type="application/json",
        )
        second_response = self.client.post(
            reservation_url(product.id),
            data={"quantity": 2},
            content_type="application/json",
        )

        product.refresh_from_db()
        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(problem_body(first_response), {"product_id": product.id, "stock": 8})
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(problem_body(second_response), {"product_id": product.id, "stock": 6})
        self.assertEqual(product.stock, 6)


class ProductStockReservationConcurrencyApiTests(TransactionTestCase):
    reset_sequences = True

    def test_concurrent_reservations_do_not_oversell_or_leak_database_lock_errors(self):
        product = Product.objects.create(name="Widget", price=1000, stock=1)
        barrier = threading.Barrier(2)
        responses = []

        def reserve_once():
            close_old_connections()
            client = Client()
            barrier.wait(timeout=5)
            response = client.post(
                reservation_url(product.id),
                data=json.dumps({"quantity": 1}),
                content_type="application/json",
            )
            responses.append(response)
            close_old_connections()

        threads = [threading.Thread(target=reserve_once) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)

        product.refresh_from_db()
        statuses = [response.status_code for response in responses]
        problem_types = [
            problem_body(response)["type"]
            for response in responses
            if response.status_code == 409
        ]

        self.assertEqual(len(responses), 2)
        self.assertLessEqual(statuses.count(200), 1)
        self.assertTrue(all(status in {200, 409} for status in statuses))
        self.assertGreaterEqual(product.stock, 0)
        self.assertIn(product.stock, {0, 1})
        self.assertTrue(
            all(
                problem_type
                in {
                    "/problems/insufficient-product-stock",
                    "/problems/product-stock-reservation-conflict",
                }
                for problem_type in problem_types
            )
        )
