import unittest

from application.catalog.application_layer.create_order.command.create_order_app import (
    CreateOrderApp,
)
from application.catalog.application_layer.create_order.dto.create_order_command import (
    CreateOrderCommand,
)
from application.catalog.domain_layer.order.entity.order import Order
from application.catalog.domain_layer.product.value_object.accepted_stock import (
    AcceptedStock,
)


class CreateOrderAppTests(unittest.TestCase):
    def test_creates_order_from_accepted_stock_and_commits_unit_of_work(self):
        uow = FakeCatalogUnitOfWork(
            accepted_stock=AcceptedStock(
                product_id=1,
                accepted_quantity=2,
                unit_price=1500,
            )
        )
        app = CreateOrderApp(uow)

        result = app.create(CreateOrderCommand(product_id=1, quantity=2))

        self.assertEqual(result.product_id, 1)
        self.assertEqual(result.quantity, 2)
        self.assertEqual(result.unit_price, 1500)
        self.assertEqual(uow.product_repository.accepted_requests, [(1, 2)])
        self.assertEqual(len(uow.order_repository.saved_orders), 1)
        self.assertTrue(uow.committed)

    def test_rolls_back_unit_of_work_when_stock_acceptance_fails(self):
        uow = FakeCatalogUnitOfWork(error=RuntimeError("stock failure"))
        app = CreateOrderApp(uow)

        with self.assertRaises(RuntimeError):
            app.create(CreateOrderCommand(product_id=1, quantity=2))

        self.assertFalse(uow.committed)
        self.assertTrue(uow.rolled_back)
        self.assertEqual(uow.order_repository.saved_orders, [])

    def test_rejects_command_with_non_positive_product_id(self):
        with self.assertRaises(ValueError):
            CreateOrderCommand(product_id=0, quantity=1)

    def test_rejects_command_with_non_positive_quantity(self):
        with self.assertRaises(ValueError):
            CreateOrderCommand(product_id=1, quantity=0)

    def test_rejects_order_with_invalid_invariants(self):
        invalid_orders = [
            {"product_id": 0, "quantity": 1, "unit_price": 1000},
            {"product_id": 1, "quantity": 0, "unit_price": 1000},
            {"product_id": 1, "quantity": 1, "unit_price": -1},
        ]

        for invalid_order in invalid_orders:
            with self.subTest(invalid_order=invalid_order):
                with self.assertRaises(ValueError):
                    Order(**invalid_order)

    def test_rejects_accepted_stock_with_invalid_invariants(self):
        invalid_accepted_stocks = [
            {"product_id": 0, "accepted_quantity": 1, "unit_price": 1000},
            {"product_id": 1, "accepted_quantity": 0, "unit_price": 1000},
            {"product_id": 1, "accepted_quantity": 1, "unit_price": -1},
        ]

        for invalid_accepted_stock in invalid_accepted_stocks:
            with self.subTest(invalid_accepted_stock=invalid_accepted_stock):
                with self.assertRaises(ValueError):
                    AcceptedStock(**invalid_accepted_stock)


class FakeCatalogUnitOfWork:
    def __init__(self, accepted_stock=None, error=None):
        self.product_repository = FakeProductRepository(accepted_stock, error)
        self.order_repository = FakeOrderRepository()
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            return False
        self.rollback()
        return False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


class FakeProductRepository:
    def __init__(self, accepted_stock, error):
        self.accepted_stock = accepted_stock
        self.error = error
        self.accepted_requests = []

    def accept_stock(self, product_id, quantity):
        self.accepted_requests.append((product_id, quantity))
        if self.error is not None:
            raise self.error
        return self.accepted_stock


class FakeOrderRepository:
    def __init__(self):
        self.saved_orders = []

    def add(self, order):
        self.saved_orders.append(order)
        return Order(
            product_id=order.product_id,
            quantity=order.quantity,
            unit_price=order.unit_price,
            id=10,
            created_at="2026-05-28T10:30:00Z",
        )
