from types import TracebackType
from typing import Optional

from django.test import SimpleTestCase

from application.catalog.application_layer.create_order.command.create_order_app import (
    CreateOrderApp,
)
from application.catalog.application_layer.create_order.dto.create_order_command import (
    CreateOrderCommand,
)
from application.catalog.domain_layer.order.order import Order
from application.catalog.domain_layer.product.exception import InsufficientStock, ProductNotFound


class FakeProductRepository:
    def __init__(
        self,
        *,
        product_id: int = 1,
        unit_price: int = 5000,
        remaining_stock: int = 3,
        exception: Optional[Exception] = None,
    ) -> None:
        self.product_id = product_id
        self.unit_price = unit_price
        self.remaining_stock = remaining_stock
        self.exception = exception

    def reserve(self, product_id: int, quantity: int) -> tuple[int, int, int]:
        if self.exception is not None:
            raise self.exception
        return self.product_id, self.unit_price, self.remaining_stock


class FakeOrderRepository:
    def __init__(self, order_id: int = 11) -> None:
        self.order_id = order_id
        self.saved_order: Optional[Order] = None

    def save(self, order: Order) -> int:
        self.saved_order = order
        return self.order_id


class ImmediateTransaction:
    def __enter__(self) -> None:
        return None

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        return False


class CreateOrderAppTests(SimpleTestCase):
    def test_create_order_reserves_stock_and_saves_order(self) -> None:
        product_repository = FakeProductRepository()
        order_repository = FakeOrderRepository(order_id=20)
        app = CreateOrderApp(
            product_repository=product_repository,
            order_repository=order_repository,
            transaction_factory=ImmediateTransaction,
        )

        result = app.create(CreateOrderCommand(product_id=1, quantity=2))

        self.assertEqual(result.order_id, 20)
        self.assertEqual(result.product_id, 1)
        self.assertEqual(result.quantity, 2)
        self.assertEqual(result.unit_price, 5000)
        self.assertEqual(result.total_price, 10000)
        self.assertEqual(result.remaining_stock, 3)
        self.assertEqual(order_repository.saved_order.quantity, 2)

    def test_create_order_propagates_insufficient_stock_without_saving_order(self) -> None:
        order_repository = FakeOrderRepository()
        app = CreateOrderApp(
            product_repository=FakeProductRepository(
                exception=InsufficientStock(product_id=1, requested_quantity=5, available_stock=3)
            ),
            order_repository=order_repository,
            transaction_factory=ImmediateTransaction,
        )

        with self.assertRaises(InsufficientStock):
            app.create(CreateOrderCommand(product_id=1, quantity=5))

        self.assertIsNone(order_repository.saved_order)

    def test_create_order_propagates_product_not_found_without_saving_order(self) -> None:
        order_repository = FakeOrderRepository()
        app = CreateOrderApp(
            product_repository=FakeProductRepository(exception=ProductNotFound(product_id=999)),
            order_repository=order_repository,
            transaction_factory=ImmediateTransaction,
        )

        with self.assertRaises(ProductNotFound):
            app.create(CreateOrderCommand(product_id=999, quantity=1))

        self.assertIsNone(order_repository.saved_order)
