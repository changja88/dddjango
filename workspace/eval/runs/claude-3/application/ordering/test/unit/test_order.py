"""Order 애그리거트·Quantity VO 단위 테스트 (안쪽 루프).

근거: 설계 명세 §1.2(Order 애그리거트)·§1.1(Quantity VO)·§1.3(도메인 예외).
순수 단위 테스트 — DB·프레임워크 없이 도메인 규칙(수량 불변식·총액 계산·
가격 스냅샷·상태)만 검증한다.
"""
from datetime import datetime, timezone

from django.test import SimpleTestCase

from application.ordering.domain_layer.order.exception import InvalidQuantity, OutOfStock
from application.ordering.domain_layer.order.order import Order, OrderStatus
from application.ordering.domain_layer.order.value_object.quantity import Quantity


class QuantityTest(SimpleTestCase):
    """수량 값 객체의 자기검증 불변식 (명세 §1.1)."""

    def test_accepts_positive_value(self) -> None:
        quantity = Quantity(3)

        self.assertEqual(quantity.value, 3)

    def test_rejects_zero(self) -> None:
        with self.assertRaises(InvalidQuantity):
            Quantity(0)

    def test_rejects_negative(self) -> None:
        with self.assertRaises(InvalidQuantity):
            Quantity(-1)

    def test_is_immutable(self) -> None:
        quantity = Quantity(2)

        with self.assertRaises(Exception):
            quantity.value = 5  # type: ignore[misc]


class OutOfStockTest(SimpleTestCase):
    """OutOfStock 는 요청 수량을 담는다 (409 requested 에코 — 명세 §2.3)."""

    def test_carries_requested_quantity(self) -> None:
        exc = OutOfStock(requested=5, detail="재고 부족")

        self.assertEqual(exc.requested, 5)

    def test_detail_is_str_representation(self) -> None:
        exc = OutOfStock(requested=5, detail="재고 부족: 가용 3, 요청 5")

        self.assertIn("요청 5", str(exc))


class OrderPlaceTest(SimpleTestCase):
    """Order.place 팩토리: 총액 계산·가격 스냅샷·상태 (명세 §1.2)."""

    def test_place_computes_total_price_from_unit_price_and_quantity(self) -> None:
        now = datetime(2026, 5, 29, tzinfo=timezone.utc)

        order = Order.place(product_id=42, quantity=Quantity(3), unit_price=1000, now=now)

        self.assertEqual(order.product_id, 42)
        self.assertEqual(order.quantity.value, 3)
        self.assertEqual(order.unit_price, 1000)
        self.assertEqual(order.total_price, 3000)

    def test_place_starts_in_placed_status(self) -> None:
        now = datetime(2026, 5, 29, tzinfo=timezone.utc)

        order = Order.place(product_id=1, quantity=Quantity(1), unit_price=500, now=now)

        self.assertEqual(order.status, OrderStatus.PLACED)

    def test_place_records_created_at(self) -> None:
        now = datetime(2026, 5, 29, tzinfo=timezone.utc)

        order = Order.place(product_id=1, quantity=Quantity(2), unit_price=500, now=now)

        self.assertEqual(order.created_at, now)

    def test_place_has_no_id_before_persistence(self) -> None:
        now = datetime(2026, 5, 29, tzinfo=timezone.utc)

        order = Order.place(product_id=1, quantity=Quantity(2), unit_price=500, now=now)

        self.assertIsNone(order.id)
