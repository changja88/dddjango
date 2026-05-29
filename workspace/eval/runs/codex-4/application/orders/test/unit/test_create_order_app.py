from django.test import SimpleTestCase

from application.orders.application_layer.create_order.command.create_order_app import (
    CreateOrderApp,
)
from application.orders.application_layer.create_order.dto.create_order_command import (
    CreateOrderCommand,
)
from application.orders.domain_layer.order.exception import InsufficientStock
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.port.product_inventory_port import (
    InventoryConflict,
    ProductInventorySnapshot,
)


class FakeOrderRepository:
    def __init__(self) -> None:
        self.saved_orders = []

    def save(self, order):
        saved_order = Order(
            id=101,
            product_id=order.product_id,
            quantity=order.quantity,
            status=order.status,
        )
        self.saved_orders.append(saved_order)
        return saved_order


class FakeProductInventoryPort:
    def __init__(self, snapshots, conflicts_before_success=0) -> None:
        self.snapshots = list(snapshots)
        self.conflicts_before_success = conflicts_before_success
        self.decrement_attempts = []

    def load_snapshot(self, product_id):
        return self.snapshots.pop(0)

    def decrement_stock(self, snapshot, quantity) -> None:
        self.decrement_attempts.append((snapshot, quantity))
        if self.conflicts_before_success > 0:
            self.conflicts_before_success -= 1
            raise InventoryConflict("stale inventory")


class PassthroughTransactionRunner:
    def run(self, operation):
        return operation()


class CreateOrderAppTests(SimpleTestCase):
    def test_persists_order_after_successful_inventory_decrement(self) -> None:
        order_repository = FakeOrderRepository()
        inventory_port = FakeProductInventoryPort(
            [ProductInventorySnapshot(product_id=7, available_stock=5, version=1)]
        )
        app = CreateOrderApp(
            order_repository=order_repository,
            product_inventory_port=inventory_port,
            transaction_runner=PassthroughTransactionRunner(),
        )

        result = app.execute(CreateOrderCommand(product_id=7, quantity=2))

        self.assertEqual(result.id, 101)
        self.assertEqual(result.product_id, 7)
        self.assertEqual(result.quantity, 2)
        self.assertEqual(result.status, "created")
        self.assertEqual(len(inventory_port.decrement_attempts), 1)
        self.assertEqual(len(order_repository.saved_orders), 1)

    def test_retries_conflict_with_fresh_snapshot_and_surfaces_insufficient_stock(
        self,
    ) -> None:
        order_repository = FakeOrderRepository()
        inventory_port = FakeProductInventoryPort(
            [
                ProductInventorySnapshot(product_id=7, available_stock=5, version=1),
                ProductInventorySnapshot(product_id=7, available_stock=1, version=2),
            ],
            conflicts_before_success=1,
        )
        app = CreateOrderApp(
            order_repository=order_repository,
            product_inventory_port=inventory_port,
            transaction_runner=PassthroughTransactionRunner(),
        )

        with self.assertRaises(InsufficientStock):
            app.execute(CreateOrderCommand(product_id=7, quantity=2))

        self.assertEqual(len(inventory_port.decrement_attempts), 1)
        self.assertEqual(order_repository.saved_orders, [])

    def test_surfaces_inventory_conflict_when_retry_also_conflicts(self) -> None:
        order_repository = FakeOrderRepository()
        inventory_port = FakeProductInventoryPort(
            [
                ProductInventorySnapshot(product_id=7, available_stock=5, version=1),
                ProductInventorySnapshot(product_id=7, available_stock=5, version=2),
            ],
            conflicts_before_success=2,
        )
        app = CreateOrderApp(
            order_repository=order_repository,
            product_inventory_port=inventory_port,
            transaction_runner=PassthroughTransactionRunner(),
        )

        with self.assertRaisesMessage(InventoryConflict, "inventory conflict after retry"):
            app.execute(CreateOrderCommand(product_id=7, quantity=2))

        self.assertEqual(len(inventory_port.decrement_attempts), 2)
        self.assertEqual(order_repository.saved_orders, [])
