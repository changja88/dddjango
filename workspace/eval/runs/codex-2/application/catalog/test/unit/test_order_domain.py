from django.test import SimpleTestCase

from application.catalog.domain_layer.order.exception import InvalidOrderQuantity
from application.catalog.domain_layer.order.order import Order


class OrderDomainTests(SimpleTestCase):
    def test_create_calculates_total_price(self) -> None:
        order = Order.create(product_id=10, quantity=2, unit_price=5000)

        self.assertEqual(order.product_id, 10)
        self.assertEqual(order.quantity, 2)
        self.assertEqual(order.unit_price, 5000)
        self.assertEqual(order.total_price, 10000)

    def test_create_rejects_quantity_less_than_one(self) -> None:
        with self.assertRaises(InvalidOrderQuantity):
            Order.create(product_id=10, quantity=0, unit_price=5000)


