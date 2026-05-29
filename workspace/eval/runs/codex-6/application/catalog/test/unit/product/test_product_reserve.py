from unittest import TestCase

from application.catalog.domain_layer.product.exception import (
    InsufficientStock,
    InvalidReservationQuantity,
)
from application.catalog.domain_layer.product.product import Product


class ProductReserveTests(TestCase):
    def test_reserve_decrements_stock_when_quantity_is_available(self) -> None:
        product = Product(id=1, stock=10, version=0)

        product.reserve(3)

        self.assertEqual(product.stock, 7)
        self.assertEqual(product.version, 0)

    def test_reserve_rejects_quantity_greater_than_stock_without_changing_stock(self) -> None:
        product = Product(id=1, stock=2, version=0)

        with self.assertRaises(InsufficientStock) as context:
            product.reserve(3)

        self.assertEqual(product.stock, 2)
        self.assertEqual(context.exception.requested_quantity, 3)
        self.assertEqual(context.exception.available_stock, 2)

    def test_reserve_rejects_non_positive_quantity_without_changing_stock(self) -> None:
        product = Product(id=1, stock=5, version=0)

        with self.assertRaises(InvalidReservationQuantity):
            product.reserve(0)

        self.assertEqual(product.stock, 5)
