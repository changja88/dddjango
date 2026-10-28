"""ok_test_imports_part — 시험은 부품 모듈을 가져와도 된다(#662 는 시험 아닌 제품 코드만 본다)."""
from __future__ import annotations

from application.orders.application_layer.order.checkout_order.checkout_order_use_case.card_payment import CardPayment


def test_card_payment_is_a_part() -> None:
    assert CardPayment.__name__ == "CardPayment"
