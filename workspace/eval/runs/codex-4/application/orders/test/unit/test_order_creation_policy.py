from django.test import SimpleTestCase

from application.orders.domain_layer.order.exception import (
    InsufficientStock,
    InvalidQuantity,
)
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.port.product_inventory_port import (
    ProductInventorySnapshot,
)
from application.orders.domain_layer.order.value_object.quantity import Quantity


class OrderCreationPolicyTests(SimpleTestCase):
    def test_creates_order_when_inventory_has_enough_stock(self):
        snapshot = ProductInventorySnapshot(product_id=12, available_stock=5, version=3)
        quantity = Quantity(2)

        order = Order.create(product_id=12, quantity=quantity, inventory_snapshot=snapshot)

        self.assertEqual(order.product_id, 12)
        self.assertEqual(order.quantity, 2)
        self.assertEqual(order.status, "created")

    def test_rejects_when_inventory_stock_is_insufficient(self):
        snapshot = ProductInventorySnapshot(product_id=12, available_stock=1, version=3)

        with self.assertRaises(InsufficientStock) as raised:
            Order.create(
                product_id=12,
                quantity=Quantity(2),
                inventory_snapshot=snapshot,
            )

        self.assertEqual(raised.exception.available_stock, 1)
        self.assertEqual(raised.exception.requested_quantity, 2)

    def test_quantity_must_be_positive_integer(self):
        invalid_values = [0, -1, "2", 1.5]

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaises(InvalidQuantity):
                    Quantity(invalid_value)
