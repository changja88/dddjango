from decimal import Decimal

from django.test import TestCase

from catalog.models import Product
from catalog.services import InsufficientStock, reserve_product_stock


class ProductReserveTests(TestCase):
    def test_reserve_subtracts_quantity_from_stock(self):
        product = Product(name="Unit Product", price=Decimal("19.99"), stock=5)

        product.reserve(3)

        self.assertEqual(product.stock, 2)

    def test_reserve_rejects_quantity_greater_than_stock(self):
        product = Product(name="Unit Product", price=Decimal("19.99"), stock=2)

        with self.assertRaises(InsufficientStock):
            product.reserve(3)

        self.assertEqual(product.stock, 2)


class ReserveProductStockServiceTests(TestCase):
    def test_insufficient_stock_does_not_change_persisted_stock(self):
        product = Product.objects.create(name="Unit Product", price=Decimal("19.99"), stock=2)

        with self.assertRaises(InsufficientStock):
            reserve_product_stock(product.pk, 3)

        product.refresh_from_db()
        self.assertEqual(product.stock, 2)
