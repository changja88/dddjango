"""단위 테스트: 도메인 Order 생성·수량 검증.

Order는 다른 애그리거트(Product)를 ID로만 참조하고(product_id),
자기 식별자·상태·수량의 일관성만 책임진다(설계 명세 section 1.2).
"""

import pytest

from catalog.domain.order import Order


def test_order_created_with_default_status():
    order = Order(product_id=1, quantity=3)

    assert order.status == "CREATED"


def test_order_holds_product_id_and_quantity():
    order = Order(product_id=42, quantity=7)

    assert order.product_id == 42
    assert order.quantity == 7


@pytest.mark.parametrize("quantity", [0, -1, -5])
def test_order_rejects_non_positive_quantity(quantity):
    with pytest.raises(ValueError):
        Order(product_id=1, quantity=quantity)
