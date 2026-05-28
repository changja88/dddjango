import json
from typing import NoReturn
from unittest.mock import patch

from django.apps import apps
from django.db.models import Model
from django.http import HttpResponse
from django.test import Client, TestCase

from application.catalog.domain_layer.product.exception import DatabaseBusy


ORDERS_URL = "/api/orders/"


class CreateOrderApiAcceptanceTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_creates_order_and_decrements_stock_when_stock_is_sufficient(self) -> None:
        product = product_model().objects.create(name="Notebook", price=5000, stock=5)

        response = self.client.post(
            ORDERS_URL,
            data={"product_id": product.id, "quantity": 2},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertResponseContentType(response, "application/json")
        body = response.json()
        self.assertIsInstance(body["order_id"], int)
        self.assertEqual(body["product_id"], product.id)
        self.assertEqual(body["quantity"], 2)
        self.assertEqual(body["unit_price"], 5000)
        self.assertEqual(body["total_price"], 10000)
        self.assertEqual(body["remaining_stock"], 3)

        product.refresh_from_db()
        self.assertEqual(product.stock, 3)

        order = order_model().objects.get()
        self.assertEqual(order.id, body["order_id"])
        self.assertEqual(order.product_id, product.id)
        self.assertEqual(order.quantity, 2)
        self.assertEqual(order.unit_price, 5000)

    def test_returns_409_and_preserves_data_when_stock_is_insufficient(self) -> None:
        product = product_model().objects.create(name="Notebook", price=5000, stock=3)

        response = self.client.post(
            ORDERS_URL,
            data={"product_id": product.id, "quantity": 5},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 409)
        self.assertProblemDetails(response, "/problems/insufficient-stock", 409)
        body = response.json()
        self.assertEqual(body["product_id"], product.id)
        self.assertEqual(body["requested_quantity"], 5)
        self.assertEqual(body["available_stock"], 3)

        product.refresh_from_db()
        self.assertEqual(product.stock, 3)
        self.assertEqual(order_model().objects.count(), 0)

    def test_returns_404_when_product_does_not_exist(self) -> None:
        response = self.client.post(
            ORDERS_URL,
            data={"product_id": 999999, "quantity": 1},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertProblemDetails(response, "/problems/product-not-found", 404)
        self.assertEqual(response.json()["product_id"], 999999)
        self.assertEqual(order_model().objects.count(), 0)

    def test_returns_400_for_invalid_request_body(self) -> None:
        cases = (
            ("malformed json", "{", "application/json"),
            ("missing product id", {"quantity": 1}, "application/json"),
            ("wrong field type", {"product_id": "not-an-int", "quantity": 1}, "application/json"),
        )

        for _label, payload, content_type in cases:
            with self.subTest(_label):
                response = self.client.post(
                    ORDERS_URL,
                    data=payload if isinstance(payload, str) else json.dumps(payload),
                    content_type=content_type,
                )

                self.assertEqual(response.status_code, 400)
                self.assertProblemDetails(response, "/problems/invalid-request", 400)
                self.assertEqual(order_model().objects.count(), 0)

    def test_returns_422_for_invalid_quantity(self) -> None:
        product = product_model().objects.create(name="Notebook", price=5000, stock=3)

        response = self.client.post(
            ORDERS_URL,
            data={"product_id": product.id, "quantity": 0},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)
        self.assertProblemDetails(response, "/problems/invalid-order-quantity", 422)
        product.refresh_from_db()
        self.assertEqual(product.stock, 3)
        self.assertEqual(order_model().objects.count(), 0)

    def test_returns_415_for_unsupported_media_type(self) -> None:
        response = self.client.post(
            ORDERS_URL,
            data="product_id=1&quantity=1",
            content_type="application/x-www-form-urlencoded",
        )

        self.assertEqual(response.status_code, 415)
        self.assertProblemDetails(response, "/problems/unsupported-media-type", 415)
        self.assertEqual(order_model().objects.count(), 0)

    def test_returns_503_problem_details_when_database_is_busy(self) -> None:
        class BusyCreateOrderApp:
            def __init__(self, *args: object, **kwargs: object) -> None:
                pass

            def create(self, _command: object) -> NoReturn:
                raise DatabaseBusy("Database is temporarily busy.")

        with patch(
            "application.catalog.presentation_layer.api.create_order.api_orders.CreateOrderApp",
            BusyCreateOrderApp,
        ):
            response = self.client.post(
                ORDERS_URL,
                data={"product_id": 1, "quantity": 1},
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 503)
        self.assertProblemDetails(response, "/problems/database-busy", 503)
        self.assertEqual(order_model().objects.count(), 0)

    def assertProblemDetails(self, response: HttpResponse, problem_type: str, status_code: int) -> None:
        self.assertResponseContentType(response, "application/problem+json")
        body = response.json()
        self.assertEqual(body["type"], problem_type)
        self.assertEqual(body["status"], status_code)
        self.assertIsInstance(body["title"], str)
        self.assertIsInstance(body["detail"], str)

    def assertResponseContentType(self, response: HttpResponse, expected_content_type: str) -> None:
        content_type = response.headers["Content-Type"].split(";")[0]
        self.assertEqual(content_type, expected_content_type)


def product_model() -> type[Model]:
    return apps.get_model("catalog", "ProductModel")


def order_model() -> type[Model]:
    return apps.get_model("catalog", "OrderModel")
