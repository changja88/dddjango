from django.test import SimpleTestCase

from catalog.exceptions import InsufficientStock, InvalidOrderQuantity
from catalog.models import Order, Product


class ProductStockDeductionTests(SimpleTestCase):
    def test_deduct_stock_reduces_stock_when_quantity_is_available(self) -> None:
        product = Product(name="Desk", price=1200, stock=5)

        remaining_stock = product.deduct_stock(2)

        self.assertEqual(remaining_stock, 3)
        self.assertEqual(product.stock, 3)

    def test_deduct_stock_rejects_non_positive_quantity(self) -> None:
        product = Product(name="Desk", price=1200, stock=5)

        with self.assertRaises(InvalidOrderQuantity):
            product.deduct_stock(0)

        self.assertEqual(product.stock, 5)

    def test_deduct_stock_rejects_quantity_greater_than_stock(self) -> None:
        product = Product(name="Desk", price=1200, stock=1)

        with self.assertRaises(InsufficientStock):
            product.deduct_stock(2)

        self.assertEqual(product.stock, 1)


class OrderSnapshotTests(SimpleTestCase):
    def test_for_product_captures_unit_price_and_total_price(self) -> None:
        product = Product(id=7, name="Desk", price=1200, stock=5)

        order = Order.for_product(product=product, quantity=2)

        self.assertEqual(order.product_id, 7)
        self.assertEqual(order.quantity, 2)
        self.assertEqual(order.unit_price, 1200)
        self.assertEqual(order.total_price, 2400)

    def test_for_product_rejects_non_positive_quantity(self) -> None:
        product = Product(id=7, name="Desk", price=1200, stock=5)

        with self.assertRaises(InvalidOrderQuantity):
            Order.for_product(product=product, quantity=0)
