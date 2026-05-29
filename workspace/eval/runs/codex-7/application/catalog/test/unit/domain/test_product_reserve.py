from django.test import SimpleTestCase

from application.catalog.domain_layer.product.exception import (
    InsufficientStock,
    InvalidReservationQuantity,
)
from application.catalog.domain_layer.product.product import Product


class ProductReserveTests(SimpleTestCase):
    def test_reserve_decrements_stock_when_quantity_is_available(self):
        product = Product(id=1, name="Widget", price=1000, stock=10)

        product.reserve(3)

        self.assertEqual(product.stock, 7)

    def test_reserve_rejects_insufficient_stock_without_changing_stock(self):
        product = Product(id=1, name="Widget", price=1000, stock=2)

        with self.assertRaises(InsufficientStock) as context:
            product.reserve(3)

        self.assertEqual(context.exception.available_stock, 2)
        self.assertEqual(context.exception.requested_quantity, 3)
        self.assertEqual(product.stock, 2)

    def test_product_cannot_be_constructed_with_negative_stock(self):
        with self.assertRaises(ValueError):
            Product(id=1, name="Widget", price=1000, stock=-1)

    def test_reserve_rejects_non_positive_quantity(self):
        product = Product(id=1, name="Widget", price=1000, stock=10)

        with self.assertRaises(InvalidReservationQuantity):
            product.reserve(0)

