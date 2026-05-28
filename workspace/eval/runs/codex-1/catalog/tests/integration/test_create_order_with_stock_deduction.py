from __future__ import annotations

import threading
from typing import Any
from unittest.mock import patch

from django.db import IntegrityError, close_old_connections
from django.test import TestCase, TransactionTestCase

from catalog.models import Product


def create_order(product_id: int, quantity: int) -> Any:
    from catalog.services import create_order as create_order_service

    return create_order_service(product_id=product_id, quantity=quantity)


def order_model() -> type[Any]:
    from catalog.models import Order

    return Order


def exception_type(name: str) -> type[Exception]:
    from catalog import exceptions

    return getattr(exceptions, name)


def result_value(result: Any, field_name: str) -> Any:
    if isinstance(result, dict):
        return result[field_name]
    return getattr(result, field_name)


class CreateOrderWithStockDeductionAcceptanceTests(TestCase):
    def test_creates_order_and_deducts_stock_when_stock_is_sufficient(self) -> None:
        product = Product.objects.create(name="Desk", price=1200, stock=5)

        result = create_order(product_id=product.id, quantity=2)

        product.refresh_from_db()
        order = order_model().objects.get(id=result_value(result, "order_id"))
        self.assertEqual(product.stock, 3)
        self.assertEqual(order.product_id, product.id)
        self.assertEqual(order.quantity, 2)
        self.assertEqual(order.unit_price, 1200)
        self.assertEqual(order.total_price, 2400)
        self.assertEqual(result_value(result, "product_id"), product.id)
        self.assertEqual(result_value(result, "quantity"), 2)
        self.assertEqual(result_value(result, "unit_price"), 1200)
        self.assertEqual(result_value(result, "total_price"), 2400)
        self.assertEqual(result_value(result, "remaining_stock"), 3)

    def test_creates_order_and_leaves_zero_stock_when_stock_exactly_matches_quantity(self) -> None:
        product = Product.objects.create(name="Chair", price=800, stock=3)

        result = create_order(product_id=product.id, quantity=3)

        product.refresh_from_db()
        order = order_model().objects.get(id=result_value(result, "order_id"))
        self.assertEqual(product.stock, 0)
        self.assertEqual(order.quantity, 3)
        self.assertEqual(order.total_price, 2400)
        self.assertEqual(result_value(result, "remaining_stock"), 0)

    def test_rejects_order_and_preserves_stock_when_stock_is_insufficient(self) -> None:
        product = Product.objects.create(name="Lamp", price=500, stock=1)
        Order = order_model()

        with self.assertRaises(exception_type("InsufficientStock")):
            create_order(product_id=product.id, quantity=2)

        product.refresh_from_db()
        self.assertEqual(product.stock, 1)
        self.assertEqual(Order.objects.count(), 0)

    def test_rejects_order_when_product_does_not_exist(self) -> None:
        Order = order_model()

        with self.assertRaises(exception_type("ProductNotFound")):
            create_order(product_id=999_999, quantity=1)

        self.assertEqual(Order.objects.count(), 0)

    def test_rejects_non_positive_quantity_and_preserves_stock(self) -> None:
        product = Product.objects.create(name="Shelf", price=300, stock=4)
        Order = order_model()

        for quantity in (0, -1):
            with self.subTest(quantity=quantity):
                with self.assertRaises(exception_type("InvalidOrderQuantity")):
                    create_order(product_id=product.id, quantity=quantity)

                product.refresh_from_db()
                self.assertEqual(product.stock, 4)
                self.assertEqual(Order.objects.count(), 0)

    def test_order_keeps_price_snapshot_when_product_price_changes_later(self) -> None:
        product = Product.objects.create(name="Table", price=275, stock=6)

        result = create_order(product_id=product.id, quantity=4)
        product.price = 999
        product.save(update_fields=["price"])

        order = order_model().objects.get(id=result_value(result, "order_id"))
        self.assertEqual(order.unit_price, 275)
        self.assertEqual(order.total_price, 1100)
        self.assertEqual(result_value(result, "unit_price"), 275)
        self.assertEqual(result_value(result, "total_price"), 1100)

    def test_order_total_price_is_protected_by_database_invariant(self) -> None:
        product = Product.objects.create(name="Cabinet", price=200, stock=10)
        Order = order_model()

        with self.assertRaises(IntegrityError):
            Order.objects.create(
                product=product,
                quantity=2,
                unit_price=200,
                total_price=999,
            )

    def test_rolls_back_stock_deduction_when_order_creation_fails(self) -> None:
        product = Product.objects.create(name="Bookcase", price=700, stock=5)
        Order = order_model()

        with patch.object(Order, "save", side_effect=RuntimeError("simulated order failure")):
            with self.assertRaises(RuntimeError):
                create_order(product_id=product.id, quantity=2)

        product.refresh_from_db()
        self.assertEqual(product.stock, 5)
        self.assertEqual(Order.objects.count(), 0)


class ConcurrentCreateOrderAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def test_concurrent_orders_cannot_deduct_more_than_available_stock(self) -> None:
        product = Product.objects.create(name="Monitor", price=1000, stock=5)
        barrier = threading.Barrier(2)
        results: list[str] = []
        errors: list[BaseException] = []
        lock = threading.Lock()
        insufficient_stock = exception_type("InsufficientStock")

        def submit_order() -> None:
            close_old_connections()
            try:
                barrier.wait(timeout=5)
                create_order(product_id=product.id, quantity=3)
            except insufficient_stock:
                with lock:
                    results.append("insufficient_stock")
            except BaseException as exc:
                with lock:
                    errors.append(exc)
            else:
                with lock:
                    results.append("created")
            finally:
                close_old_connections()

        threads = [threading.Thread(target=submit_order) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)

        self.assertFalse(errors)
        self.assertCountEqual(results, ["created", "insufficient_stock"])

        product.refresh_from_db()
        orders = list(order_model().objects.order_by("id"))
        self.assertEqual(product.stock, 2)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].quantity, 3)
