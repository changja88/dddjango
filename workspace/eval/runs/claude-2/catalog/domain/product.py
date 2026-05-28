"""Product 애그리거트 루트 (순수 도메인, Django 비의존).

설계 명세 section 1.2: deduct_stock의 역할은 (a) 방어 가드(quantity>=1),
(b) 차감 후 인메모리 상태 동기화와 부족 예외 표현으로 축소 재정의된다.
동시성 정확성(오버셀 차단)의 판정 권위는 인프라의 조건부 원자 UPDATE에 있다.
"""

from __future__ import annotations

from catalog.domain.exceptions import InsufficientStockError


class Product:
    def __init__(self, id: int | None, name: str, price: int, stock: int) -> None:
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

    def deduct_stock(self, quantity: int) -> None:
        """재고를 quantity만큼 차감한다.

        quantity<1이면 ValueError(방어 가드), 현재 인메모리 재고보다 크면
        InsufficientStockError를 표현한다(재고 변화 없음).
        """
        if quantity < 1:
            raise ValueError(f"quantity must be >= 1, got {quantity}.")
        if quantity > self.stock:
            raise InsufficientStockError(
                product_id=self.id if self.id is not None else 0,
                requested=quantity,
                available=self.stock,
            )
        self.stock -= quantity
