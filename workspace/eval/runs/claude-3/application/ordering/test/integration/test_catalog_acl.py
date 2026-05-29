"""DjangoProductStockPort(ACL) ↔ catalog Product 통합 테스트 (명세 §4.1·§1.4).

ACL 어댑터가 catalog Product 도메인 동작(deduct_stock)을 호출·번역하는지,
catalog 측 예외를 ordering 도메인 언어로 번역하는지 검증한다(실제 DB).
"""
from django.test import TestCase

from application.ordering.domain_layer.order.exception import OutOfStock, ProductNotFound
from application.ordering.infra_layer.acl.catalog_acl import DjangoProductStockPort
from catalog.models import Product


class GetUnitPriceTest(TestCase):
    def test_returns_current_unit_price(self) -> None:
        product = Product.objects.create(name="Widget", price=1000, stock=10)
        acl = DjangoProductStockPort()

        self.assertEqual(acl.get_unit_price(product.id), 1000)

    def test_raises_product_not_found_for_unknown_id(self) -> None:
        acl = DjangoProductStockPort()

        with self.assertRaises(ProductNotFound):
            acl.get_unit_price(999999)


class DeductTest(TestCase):
    def test_deducts_stock_via_catalog_domain_action(self) -> None:
        product = Product.objects.create(name="Widget", price=1000, stock=10)
        acl = DjangoProductStockPort()

        acl.deduct(product.id, 3)

        product.refresh_from_db()
        self.assertEqual(product.stock, 7)

    def test_translates_insufficient_stock_to_out_of_stock(self) -> None:
        product = Product.objects.create(name="Gadget", price=2000, stock=3)
        acl = DjangoProductStockPort()

        with self.assertRaises(OutOfStock) as caught:
            acl.deduct(product.id, 5)

        # 요청 수량을 OutOfStock 에 담아 409 requested 에코를 가능케 한다(명세 §2.3).
        self.assertEqual(caught.exception.requested, 5)

        product.refresh_from_db()
        self.assertEqual(product.stock, 3)

    def test_raises_product_not_found_for_unknown_id(self) -> None:
        acl = DjangoProductStockPort()

        with self.assertRaises(ProductNotFound):
            acl.deduct(999999, 1)
