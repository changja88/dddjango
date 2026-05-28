"""Acceptance (outer-loop / blackbox) tests for POST /api/v1/orders.

Single source of truth: .dddjango/order-create-with-stock/design-spec.md
These tests assert only externally observable behavior and contracts
(HTTP status, response media type, response body shape, observable stock
state changes). No implementation internals are imported -- the API is
exercised through the real mounted URL via Django's test Client.

Covered observable behaviors (design-spec section 6):
- B1: sufficient stock -> 201, order created, remaining_stock = initial - quantity
- B2: insufficient stock -> 409 problem+json, no stock change, no order created
- B3: validation failure (quantity < 1, type mismatch) -> 422 problem+json
- B4: unknown product_id -> 404 problem+json
- B5: non application/json Content-Type -> 415 problem+json
- B7: success body exposes schema_out fields only; no Location header
"""

import pytest
from django.test import Client

from catalog.models import Product

ENDPOINT = "/api/v1/orders"

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return Client()


def _post_json(client, body):
    import json

    return client.post(
        ENDPOINT,
        data=json.dumps(body),
        content_type="application/json",
    )


# --- B1: sufficient stock -> 201 + stock deducted ---------------------------


def test_create_order_with_sufficient_stock_returns_201(client):
    product = Product.objects.create(name="Widget", price=1000, stock=10)

    response = _post_json(client, {"product_id": product.id, "quantity": 3})

    assert response.status_code == 201


def test_create_order_with_sufficient_stock_deducts_stock_exactly(client):
    product = Product.objects.create(name="Widget", price=1000, stock=10)

    _post_json(client, {"product_id": product.id, "quantity": 3})

    product.refresh_from_db()
    assert product.stock == 7


def test_create_order_success_body_reports_remaining_stock(client):
    product = Product.objects.create(name="Widget", price=1000, stock=10)

    response = _post_json(client, {"product_id": product.id, "quantity": 3})
    body = response.json()

    assert body["remaining_stock"] == 7


def test_create_order_success_body_exposes_schema_out_fields(client):
    """B7: response exposes only the published schema_out fields."""
    product = Product.objects.create(name="Widget", price=1000, stock=10)

    response = _post_json(client, {"product_id": product.id, "quantity": 3})
    body = response.json()

    assert set(body.keys()) == {
        "order_id",
        "product_id",
        "quantity",
        "status",
        "remaining_stock",
    }
    assert body["product_id"] == product.id
    assert body["quantity"] == 3
    assert body["status"] == "CREATED"
    assert isinstance(body["order_id"], int)


def test_create_order_success_has_no_location_header(client):
    """B7: spec section 2.4 -- no Location header (no read endpoint)."""
    product = Product.objects.create(name="Widget", price=1000, stock=10)

    response = _post_json(client, {"product_id": product.id, "quantity": 3})

    assert response.status_code == 201
    assert "Location" not in response


# --- B2: insufficient stock -> 409, no side effects -------------------------


def test_insufficient_stock_returns_409(client):
    product = Product.objects.create(name="Widget", price=1000, stock=2)

    response = _post_json(client, {"product_id": product.id, "quantity": 5})

    assert response.status_code == 409


def test_insufficient_stock_uses_problem_json_media_type(client):
    product = Product.objects.create(name="Widget", price=1000, stock=2)

    response = _post_json(client, {"product_id": product.id, "quantity": 5})

    assert response["Content-Type"].startswith("application/problem+json")


def test_insufficient_stock_problem_body_contract(client):
    product = Product.objects.create(name="Widget", price=1000, stock=2)

    response = _post_json(client, {"product_id": product.id, "quantity": 5})
    body = response.json()

    assert body["type"] == "https://errors.example.com/catalog/insufficient-stock"
    assert body["status"] == 409
    assert body["product_id"] == product.id
    assert body["requested"] == 5
    assert body["available"] == 2


def test_insufficient_stock_does_not_change_stock(client):
    product = Product.objects.create(name="Widget", price=1000, stock=2)

    _post_json(client, {"product_id": product.id, "quantity": 5})

    product.refresh_from_db()
    assert product.stock == 2


def test_insufficient_stock_does_not_create_order(client):
    """No observable order side effect: stock unchanged and a subsequent
    valid order against the same product still deducts from the original 2."""
    product = Product.objects.create(name="Widget", price=1000, stock=2)

    _post_json(client, {"product_id": product.id, "quantity": 5})

    follow_up = _post_json(client, {"product_id": product.id, "quantity": 2})
    assert follow_up.status_code == 201
    assert follow_up.json()["remaining_stock"] == 0


# --- B4: unknown product -> 404 ---------------------------------------------


def test_unknown_product_returns_404(client):
    response = _post_json(client, {"product_id": 999999, "quantity": 1})

    assert response.status_code == 404


def test_unknown_product_uses_problem_json_media_type(client):
    response = _post_json(client, {"product_id": 999999, "quantity": 1})

    assert response["Content-Type"].startswith("application/problem+json")


def test_unknown_product_problem_body_contract(client):
    response = _post_json(client, {"product_id": 999999, "quantity": 1})
    body = response.json()

    assert body["type"] == "https://errors.example.com/catalog/product-not-found"
    assert body["status"] == 404
    assert body["product_id"] == 999999


# --- B3: validation failure -> 422 ------------------------------------------


def test_quantity_below_one_returns_422(client):
    product = Product.objects.create(name="Widget", price=1000, stock=10)

    response = _post_json(client, {"product_id": product.id, "quantity": 0})

    assert response.status_code == 422


def test_validation_failure_uses_problem_json_media_type(client):
    product = Product.objects.create(name="Widget", price=1000, stock=10)

    response = _post_json(client, {"product_id": product.id, "quantity": 0})

    assert response["Content-Type"].startswith("application/problem+json")


def test_validation_failure_problem_body_contract(client):
    product = Product.objects.create(name="Widget", price=1000, stock=10)

    response = _post_json(client, {"product_id": product.id, "quantity": 0})
    body = response.json()

    assert body["type"] == "https://errors.example.com/catalog/validation-error"
    assert body["status"] == 422
    assert "errors" in body
    assert isinstance(body["errors"], list)


def test_quantity_below_one_does_not_change_stock(client):
    product = Product.objects.create(name="Widget", price=1000, stock=10)

    _post_json(client, {"product_id": product.id, "quantity": 0})

    product.refresh_from_db()
    assert product.stock == 10


def test_negative_quantity_returns_422(client):
    product = Product.objects.create(name="Widget", price=1000, stock=10)

    response = _post_json(client, {"product_id": product.id, "quantity": -3})

    assert response.status_code == 422


def test_non_integer_quantity_returns_422(client):
    product = Product.objects.create(name="Widget", price=1000, stock=10)

    response = _post_json(client, {"product_id": product.id, "quantity": "abc"})

    assert response.status_code == 422


def test_missing_required_field_returns_422(client):
    response = _post_json(client, {"quantity": 1})

    assert response.status_code == 422


# --- B5: unsupported media type -> 415 --------------------------------------


def test_non_json_content_type_returns_415(client):
    product = Product.objects.create(name="Widget", price=1000, stock=10)

    response = client.post(
        ENDPOINT,
        data="product_id=%d&quantity=1" % product.id,
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 415


def test_unsupported_media_type_uses_problem_json_media_type(client):
    product = Product.objects.create(name="Widget", price=1000, stock=10)

    response = client.post(
        ENDPOINT,
        data="product_id=%d&quantity=1" % product.id,
        content_type="text/plain",
    )

    assert response["Content-Type"].startswith("application/problem+json")


def test_unsupported_media_type_problem_body_contract(client):
    product = Product.objects.create(name="Widget", price=1000, stock=10)

    response = client.post(
        ENDPOINT,
        data="product_id=%d&quantity=1" % product.id,
        content_type="text/plain",
    )
    body = response.json()

    assert body["type"] == "https://errors.example.com/catalog/unsupported-media-type"
    assert body["status"] == 415
