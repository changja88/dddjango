import unittest

from application.inventory.domain_layer.product.exceptions import InsufficientStock
from application.inventory.domain_layer.product.product import Product


class ProductDeductTest(unittest.TestCase):
    def test_deduct_reduces_stock(self) -> None:
        product = Product(id=1, stock=10)
        product.deduct(3)
        self.assertEqual(product.stock, 7)

    def test_deduct_rejects_when_insufficient(self) -> None:
        product = Product(id=1, stock=2)
        with self.assertRaises(InsufficientStock):
            product.deduct(5)
