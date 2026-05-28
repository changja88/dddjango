"""단위 테스트: 도메인 Product.deduct_stock 가드·상태 동기화·부족 예외 표현.

설계 명세 section 1.2 트레이드오프대로, 이 단위 테스트는 도메인 차원의
가드(quantity>=1)와 차감 후 상태 동기화·부족 예외 표현만 검증한다.
동시성 정확성(오버셀 차단)은 여기서 검증하지 않는다(통합/동시성 테스트 소유).
"""

import pytest

from catalog.domain.exceptions import InsufficientStockError
from catalog.domain.product import Product


def test_deduct_stock_reduces_in_memory_stock():
    product = Product(id=1, name="Widget", price=1000, stock=10)

    product.deduct_stock(3)

    assert product.stock == 7


def test_deduct_stock_to_zero_is_allowed():
    product = Product(id=1, name="Widget", price=1000, stock=5)

    product.deduct_stock(5)

    assert product.stock == 0


def test_deduct_stock_raises_insufficient_when_quantity_exceeds_stock():
    product = Product(id=1, name="Widget", price=1000, stock=2)

    with pytest.raises(InsufficientStockError):
        product.deduct_stock(5)


def test_deduct_stock_keeps_stock_unchanged_when_insufficient():
    product = Product(id=1, name="Widget", price=1000, stock=2)

    with pytest.raises(InsufficientStockError):
        product.deduct_stock(5)

    assert product.stock == 2


@pytest.mark.parametrize("quantity", [0, -1, -10])
def test_deduct_stock_guards_against_non_positive_quantity(quantity):
    product = Product(id=1, name="Widget", price=1000, stock=10)

    with pytest.raises(ValueError):
        product.deduct_stock(quantity)
