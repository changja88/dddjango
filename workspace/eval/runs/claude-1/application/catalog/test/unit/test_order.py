"""Order 도메인 생성자 단위 테스트 (§1.2 I4 / §5.6).

Order 생성자가 total_price = unit_price * quantity 곱을 강제하는지 검증한다.
응용이 곱을 미리 계산해 넘기지 않는다 — 생성자가 권위.
"""
from django.test import SimpleTestCase

from application.catalog.domain_layer.order.order import Order


class OrderTest(SimpleTestCase):
    def test_생성자가_total_price를_unit_price_곱하기_quantity로_강제한다(self) -> None:
        order = Order(product_id=1, quantity=2, unit_price=1000)

        self.assertEqual(order.total_price, 2000)

    def test_수량과_단가를_보유한다(self) -> None:
        order = Order(product_id=5, quantity=3, unit_price=700)

        self.assertEqual(order.product_id, 5)
        self.assertEqual(order.quantity, 3)
        self.assertEqual(order.unit_price, 700)
