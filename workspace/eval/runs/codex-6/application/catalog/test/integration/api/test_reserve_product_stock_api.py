import json
from decimal import Decimal
from typing import Any, Optional
from unittest.mock import patch

from django.test import Client, TestCase

from application.catalog.application_layer.reserve_product_stock.command.reserve_product_stock_app import (
    StockReservationConflict,
)
from catalog.models import Product


class ReserveProductStockApiTests(TestCase):
    def post_reservation(
        self,
        product_id: int,
        body: object,
        content_type: str = "application/json",
        accept: Optional[str] = None,
    ) -> Any:
        extra = {}
        if accept is not None:
            extra["HTTP_ACCEPT"] = accept

        data = body if isinstance(body, str) else json.dumps(body)
        return self.client.post(
            f"/api/catalog/products/{product_id}/stock-reservations",
            data=data,
            content_type=content_type,
            **extra,
        )

    def create_product(self, stock: int) -> Product:
        return Product.objects.create(
            name="Widget",
            price=Decimal("12.99"),
            stock=stock,
        )

    def assert_json_content_type(self, response: Any) -> None:
        self.assertEqual(response.headers["Content-Type"], "application/json")

    def assert_problem(
        self,
        response: Any,
        *,
        status_code: int,
        problem_type: str,
        title: str,
    ) -> dict[str, object]:
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.headers["Content-Type"], "application/problem+json")

        body = response.json()
        self.assertEqual(body["type"], problem_type)
        self.assertEqual(body["title"], title)
        self.assertEqual(body["status"], status_code)
        self.assertIn("detail", body)
        return body

    def assert_product_stock(self, product_id: int, expected_stock: int) -> Product:
        product = Product.objects.get(pk=product_id)
        self.assertEqual(product.stock, expected_stock)
        return product

    def test_successful_reservation_decrements_stock_and_returns_updated_stock(self) -> None:
        product = self.create_product(stock=10)
        original_version = getattr(product, "version", 0)

        response = self.post_reservation(product.pk, {"quantity": 3})

        self.assertEqual(response.status_code, 200)
        self.assert_json_content_type(response)
        self.assertEqual(response.json(), {"product_id": product.pk, "stock": 7})

        reloaded = self.assert_product_stock(product.pk, 7)
        self.assertEqual(reloaded.version, original_version + 1)

    def test_insufficient_stock_returns_409_and_preserves_stock(self) -> None:
        product = self.create_product(stock=2)
        original_version = getattr(product, "version", 0)

        response = self.post_reservation(product.pk, {"quantity": 3})

        body = self.assert_problem(
            response,
            status_code=409,
            problem_type="/problems/catalog/insufficient-stock",
            title="Insufficient stock",
        )
        self.assertEqual(body["requested_quantity"], 3)
        self.assertEqual(body["available_stock"], 2)

        reloaded = self.assert_product_stock(product.pk, 2)
        self.assertEqual(reloaded.version, original_version)

    def test_unknown_product_returns_404(self) -> None:
        response = self.post_reservation(999999, {"quantity": 1})

        body = self.assert_problem(
            response,
            status_code=404,
            problem_type="/problems/catalog/product-not-found",
            title="Product not found",
        )
        self.assertEqual(body["detail"], "Product 999999 was not found.")

    def test_missing_quantity_returns_422_and_preserves_stock(self) -> None:
        product = self.create_product(stock=5)

        response = self.post_reservation(product.pk, {})

        self.assert_problem(
            response,
            status_code=422,
            problem_type="/problems/catalog/invalid-reservation-request",
            title="Invalid reservation request",
        )
        self.assert_product_stock(product.pk, 5)

    def test_non_integer_quantity_returns_422_and_preserves_stock(self) -> None:
        product = self.create_product(stock=5)

        response = self.post_reservation(product.pk, {"quantity": "2"})

        self.assert_problem(
            response,
            status_code=422,
            problem_type="/problems/catalog/invalid-reservation-request",
            title="Invalid reservation request",
        )
        self.assert_product_stock(product.pk, 5)

    def test_non_positive_quantity_returns_422_and_preserves_stock(self) -> None:
        product = self.create_product(stock=5)

        response = self.post_reservation(product.pk, {"quantity": 0})

        self.assert_problem(
            response,
            status_code=422,
            problem_type="/problems/catalog/invalid-reservation-request",
            title="Invalid reservation request",
        )
        self.assert_product_stock(product.pk, 5)

    def test_malformed_json_returns_422_and_preserves_stock(self) -> None:
        product = self.create_product(stock=5)

        response = self.post_reservation(product.pk, "{")

        self.assert_problem(
            response,
            status_code=422,
            problem_type="/problems/catalog/invalid-reservation-request",
            title="Invalid reservation request",
        )
        self.assert_product_stock(product.pk, 5)

    def test_non_object_json_returns_422_and_preserves_stock(self) -> None:
        product = self.create_product(stock=5)

        response = self.post_reservation(product.pk, [1, 2, 3])

        self.assert_problem(
            response,
            status_code=422,
            problem_type="/problems/catalog/invalid-reservation-request",
            title="Invalid reservation request",
        )
        self.assert_product_stock(product.pk, 5)

    def test_non_json_content_type_returns_415_and_preserves_stock(self) -> None:
        product = self.create_product(stock=5)

        response = self.post_reservation(
            product.pk,
            '{"quantity": 1}',
            content_type="text/plain",
        )

        self.assert_problem(
            response,
            status_code=415,
            problem_type="/problems/catalog/unsupported-media-type",
            title="Unsupported media type",
        )
        self.assert_product_stock(product.pk, 5)

    def test_accept_header_does_not_trigger_406(self) -> None:
        product = self.create_product(stock=5)

        response = self.post_reservation(
            product.pk,
            {"quantity": 2},
            accept="text/plain",
        )

        self.assertEqual(response.status_code, 200)
        self.assert_json_content_type(response)
        self.assertEqual(response.json(), {"product_id": product.pk, "stock": 3})
        self.assert_product_stock(product.pk, 3)

    def test_reservation_api_does_not_require_csrf_token(self) -> None:
        product = self.create_product(stock=5)
        csrf_enforcing_client = Client(enforce_csrf_checks=True)

        response = csrf_enforcing_client.post(
            f"/api/catalog/products/{product.pk}/stock-reservations",
            data=json.dumps({"quantity": 2}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assert_json_content_type(response)
        self.assertEqual(response.json(), {"product_id": product.pk, "stock": 3})
        self.assert_product_stock(product.pk, 3)

    def test_stock_reservation_conflict_returns_409_problem(self) -> None:
        product = self.create_product(stock=5)

        with patch(
            "application.catalog.presentation_layer.api.reserve_product_stock."
            "api_product_stock_reservations.ReserveProductStockApp"
        ) as app_class:
            app_class.return_value.reserve.side_effect = StockReservationConflict(
                "Stock changed during reservation."
            )
            response = self.post_reservation(product.pk, {"quantity": 1})

        body = self.assert_problem(
            response,
            status_code=409,
            problem_type="/problems/catalog/stock-reservation-conflict",
            title="Stock reservation conflict",
        )
        self.assertEqual(
            body["detail"],
            "Stock changed during reservation. Retry the request.",
        )
        self.assert_product_stock(product.pk, 5)

    def test_duplicate_requests_without_idempotency_key_reserve_stock_repeatedly(self) -> None:
        product = self.create_product(stock=5)

        first_response = self.post_reservation(product.pk, {"quantity": 2})
        second_response = self.post_reservation(product.pk, {"quantity": 2})

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(first_response.json(), {"product_id": product.pk, "stock": 3})
        self.assertEqual(second_response.json(), {"product_id": product.pk, "stock": 1})
        self.assert_product_stock(product.pk, 1)
