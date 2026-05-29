"""catalog Product 재고 차감 도메인 동작 단위 테스트 (명세 OD-1·§1.4·§3.3).

deduct_stock 은 재고 충분성 판정(stock >= qty)을 소유한다 — 이 판정을
ordering 인프라 SQL 에 복제하지 않는다(명세 §1.4·§3.3 Rule ownership).
version CAS 조건부 UPDATE 는 경합 가드일 뿐이며, 판정은 항상 이 동작이 내린다.
"""
from django.test import TestCase

from catalog.exceptions import InsufficientStock
from catalog.models import Product


class DeductStockTest(TestCase):
    """재고 충분성 판정과 차감 (명세 OD-1)."""

    def test_deducts_when_stock_is_sufficient(self) -> None:
        product = Product.objects.create(name="Widget", price=1000, stock=10)

        product.deduct_stock(3)

        product.refresh_from_db()
        self.assertEqual(product.stock, 7)

    def test_deducts_exactly_to_zero(self) -> None:
        product = Product.objects.create(name="Widget", price=1000, stock=3)

        product.deduct_stock(3)

        product.refresh_from_db()
        self.assertEqual(product.stock, 0)

    def test_raises_when_stock_is_insufficient(self) -> None:
        product = Product.objects.create(name="Gadget", price=2000, stock=3)

        with self.assertRaises(InsufficientStock):
            product.deduct_stock(5)

    def test_does_not_change_stock_when_rejected(self) -> None:
        product = Product.objects.create(name="Gadget", price=2000, stock=3)

        with self.assertRaises(InsufficientStock):
            product.deduct_stock(5)

        product.refresh_from_db()
        self.assertEqual(product.stock, 3)
