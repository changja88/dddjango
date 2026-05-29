import json
import threading
from decimal import Decimal

from django.apps import apps
from django.test import Client, TestCase, TransactionTestCase


RESERVATION_PATH = "/api/products/{product_id}/reservations"
PROBLEM_JSON = "application/problem+json"


def product_model():
    return apps.get_model("catalog", "Product")


def create_product(*, stock):
    Product = product_model()
    return Product.objects.create(
        name="Acceptance Product",
        price=Decimal("19.99"),
        stock=stock,
    )


def persisted_stock(product_id):
    Product = product_model()
    return Product.objects.get(pk=product_id).stock


def post_reservation(client, product_id, body, *, content_type="application/json", accept=None):
    headers = {}
    if accept is not None:
        headers["HTTP_ACCEPT"] = accept

    if content_type == "application/json" and not isinstance(body, str):
        data = json.dumps(body)
    else:
        data = body

    return client.post(
        RESERVATION_PATH.format(product_id=product_id),
        data=data,
        content_type=content_type,
        **headers,
    )


def response_json(response):
    try:
        return json.loads(response.content.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Response body is not JSON: {response.content!r}") from exc


def assert_problem_details(testcase, response, *, status, problem_type):
    testcase.assertEqual(response.status_code, status)
    testcase.assertTrue(
        response["Content-Type"].startswith(PROBLEM_JSON),
        response["Content-Type"],
    )

    body = response_json(response)
    testcase.assertEqual(body["type"], problem_type)
    testcase.assertEqual(body["status"], status)
    testcase.assertIn("title", body)
    testcase.assertIn("detail", body)
    testcase.assertIn("instance", body)
    return body


class ProductReservationApiAcceptanceTests(TestCase):
    def test_positive_quantity_with_enough_stock_returns_200_and_remaining_stock(self):
        product = create_product(stock=10)

        response = post_reservation(self.client, product.pk, {"quantity": 3})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("application/json"))
        self.assertEqual(
            response_json(response),
            {
                "product_id": product.pk,
                "reserved_quantity": 3,
                "remaining_stock": 7,
            },
        )

    def test_successful_reservation_subtracts_requested_quantity_from_persisted_stock(self):
        product = create_product(stock=10)

        response = post_reservation(self.client, product.pk, {"quantity": 4})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(persisted_stock(product.pk), 6)

    def test_quantity_greater_than_available_stock_returns_409_and_does_not_change_stock(self):
        product = create_product(stock=2)

        response = post_reservation(self.client, product.pk, {"quantity": 3})

        assert_problem_details(
            self,
            response,
            status=409,
            problem_type="https://example.com/problems/insufficient-stock",
        )
        self.assertEqual(persisted_stock(product.pk), 2)

    def test_missing_product_returns_404_problem_details(self):
        response = post_reservation(self.client, 999_999, {"quantity": 1})

        assert_problem_details(
            self,
            response,
            status=404,
            problem_type="https://example.com/problems/product-not-found",
        )

    def test_invalid_quantity_returns_422_problem_details_with_invalid_params(self):
        product = create_product(stock=5)
        invalid_bodies = [
            ("malformed JSON", "{"),
            ("missing body", ""),
            ("non-object body", []),
            ("missing quantity", {}),
            ("non-integer quantity", {"quantity": "one"}),
            ("zero quantity", {"quantity": 0}),
            ("negative quantity", {"quantity": -1}),
        ]

        for label, body in invalid_bodies:
            with self.subTest(label=label):
                response = post_reservation(self.client, product.pk, body)

                problem = assert_problem_details(
                    self,
                    response,
                    status=422,
                    problem_type="https://example.com/problems/validation-error",
                )
                self.assertIn("invalid_params", problem)
                self.assertGreaterEqual(len(problem["invalid_params"]), 1)
                self.assertTrue(
                    all("name" in item and "reason" in item for item in problem["invalid_params"])
                )
                self.assertEqual(persisted_stock(product.pk), 5)

    def test_unsupported_request_content_type_returns_415_problem_details(self):
        product = create_product(stock=5)

        response = post_reservation(
            self.client,
            product.pk,
            "quantity=1",
            content_type="text/plain",
        )

        assert_problem_details(
            self,
            response,
            status=415,
            problem_type="https://example.com/problems/unsupported-media-type",
        )

    def test_explicit_unacceptable_accept_header_returns_406_problem_details(self):
        product = create_product(stock=5)

        unacceptable_accept_headers = [
            "text/csv",
            "application/json;q=0",
            "application/problem+json;q=0,*/*;q=0",
        ]
        for accept in unacceptable_accept_headers:
            with self.subTest(accept=accept):
                response = post_reservation(
                    self.client,
                    product.pk,
                    {"quantity": 1},
                    accept=accept,
                )

                assert_problem_details(
                    self,
                    response,
                    status=406,
                    problem_type="https://example.com/problems/not-acceptable",
                )

    def test_repeating_same_successful_post_reserves_stock_again(self):
        product = create_product(stock=5)

        first_response = post_reservation(self.client, product.pk, {"quantity": 2})
        second_response = post_reservation(self.client, product.pk, {"quantity": 2})

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(persisted_stock(product.pk), 1)


class ProductReservationConcurrencyAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def test_concurrent_reservations_do_not_create_negative_stock_or_lost_updates(self):
        product = create_product(stock=1)
        responses = []
        lock = threading.Lock()

        def reserve_once():
            response = post_reservation(Client(), product.pk, {"quantity": 1})
            with lock:
                responses.append(response.status_code)

        threads = [threading.Thread(target=reserve_once), threading.Thread(target=reserve_once)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(responses.count(200), 1)
        self.assertEqual(responses.count(409), 1)
        self.assertEqual(persisted_stock(product.pk), 0)
