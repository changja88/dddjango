"""Product.deduct() 권위 검사 단위 테스트 (§1.4 / §5.6).

도메인 권위 메서드를 DB 없이 직접 검증한다.
- I1: stock >= qty 일 때만 차감 가능.
- I2 경계: 차감 후 stock >= 0 (정확히 0이 되는 경계 포함).
- 부족 시 InsufficientStock 던지고 상태 불변.
"""
from django.test import SimpleTestCase

from application.catalog.domain_layer.product.product import Product
from application.catalog.domain_layer.product.exception import InsufficientStock


class ProductDeductTest(SimpleTestCase):
    def test_재고가_충분하면_수량만큼_차감한다(self) -> None:
        product = Product(id=1, name="위젯", price=1000, stock=10)

        product.deduct(2)

        self.assertEqual(product.stock, 8)

    def test_재고와_수량이_같으면_0까지_차감한다(self) -> None:
        # I2 경계: 차감 후 stock == 0 은 허용.
        product = Product(id=1, name="위젯", price=1000, stock=2)

        product.deduct(2)

        self.assertEqual(product.stock, 0)

    def test_재고가_부족하면_InsufficientStock을_던진다(self) -> None:
        product = Product(id=1, name="위젯", price=1000, stock=1)

        with self.assertRaises(InsufficientStock) as ctx:
            product.deduct(2)

        self.assertEqual(ctx.exception.available_stock, 1)
        self.assertEqual(ctx.exception.requested_quantity, 2)

    def test_재고가_부족하면_상태를_바꾸지_않는다(self) -> None:
        product = Product(id=1, name="위젯", price=1000, stock=1)

        with self.assertRaises(InsufficientStock):
            product.deduct(2)

        # I1 위반 → 전이 없음(불변).
        self.assertEqual(product.stock, 1)
