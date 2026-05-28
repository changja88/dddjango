from django.test import TestCase

from catalog.exceptions import InsufficientStock, ProductNotFound
from catalog.models import Order, Product
from catalog.services import create_order


class CreateOrderServiceTests(TestCase):
    def test_create_order_returns_created_order_snapshot_and_remaining_stock(self) -> None:
        product = Product.objects.create(name="Desk", price=1200, stock=5)

        result = create_order(product_id=product.id, quantity=2)

        order = Order.objects.get(id=result.order_id)
        product.refresh_from_db()
        self.assertEqual(order.total_price, 2400)
        self.assertEqual(product.stock, 3)
        self.assertEqual(result.remaining_stock, 3)

    def test_create_order_distinguishes_missing_product_from_insufficient_stock(self) -> None:
        product = Product.objects.create(name="Desk", price=1200, stock=1)

        with self.assertRaises(InsufficientStock):
            create_order(product_id=product.id, quantity=2)

        with self.assertRaises(ProductNotFound):
            create_order(product_id=999_999, quantity=1)
