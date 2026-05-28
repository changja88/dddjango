"""Order 애그리거트 루트 (순수 도메인, Django 비의존).

설계 명세 section 1.2: Order는 다른 애그리거트(Product)를 ID로만 참조하며,
자기 식별자·상태·수량의 일관성만 책임진다. 단일 상태 CREATED만 갖는다.
"""

from __future__ import annotations

STATUS_CREATED = "CREATED"


class Order:
    def __init__(
        self,
        product_id: int,
        quantity: int,
        id: int | None = None,
        status: str = STATUS_CREATED,
    ) -> None:
        if quantity < 1:
            raise ValueError(f"quantity must be >= 1, got {quantity}.")
        self.id = id
        self.product_id = product_id
        self.quantity = quantity
        self.status = status
