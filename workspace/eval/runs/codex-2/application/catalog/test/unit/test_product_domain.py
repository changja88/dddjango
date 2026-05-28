from django.test import SimpleTestCase

from application.catalog.domain_layer.product.exception import (
    InsufficientStock,
    InvalidReserveQuantity,
)
from application.catalog.domain_layer.product.product import Product


class ProductDomainTests(SimpleTestCase):
    def test_reserve_decrements_stock_when_stock_is_sufficient(self) -> None:
        product = Product(id=1, name="Notebook", price=5000, stock=5)

        product.reserve(2)

        self.assertEqual(product.stock, 3)

    def test_reserve_rejects_quantity_less_than_one(self) -> None:
        product = Product(id=1, name="Notebook", price=5000, stock=5)

        with self.assertRaises(InvalidReserveQuantity):
            product.reserve(0)

    def test_reserve_rejects_insufficient_stock_without_changing_stock(self) -> None:
        product = Product(id=1, name="Notebook", price=5000, stock=3)

        with self.assertRaises(InsufficientStock):
            product.reserve(5)

        self.assertEqual(product.stock, 3)


