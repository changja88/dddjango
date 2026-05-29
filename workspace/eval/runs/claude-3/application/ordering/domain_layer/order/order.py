"""Order 애그리거트 루트 (명세 §1.2).

단일 상품 + 수량의 주문 기록. 보호하는 불변식은 "수량 >= 1"(Quantity VO 위임)과
"가격 스냅샷·총액은 생성 후 불변"이다. 재고(stock) 불변식은 Order 의 경계가 아니다
(재고는 catalog Product 소유 — 명세 §1.2 규칙1·규칙3). 타 애그리거트(Product)는
객체가 아니라 product_id(int)로만 참조한다(규칙3).
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from application.ordering.domain_layer.order.value_object.quantity import Quantity


class OrderStatus(str, Enum):
    """주문 생명주기 상태. 이번 범위에선 생성 직후 PLACED 단일 상태(전이 없음)."""

    PLACED = "PLACED"


class Order:
    """주문 애그리거트 루트.

    총액 계산·상태 결정을 도메인이 소유한다(빈혈 차단 — 명세 §1.2·§3.2).
    외부에서 total_price 를 주입받지 않는다.
    """

    def __init__(
        self,
        *,
        product_id: int,
        quantity: Quantity,
        unit_price: int,
        status: OrderStatus,
        created_at: datetime,
        id: Optional[int] = None,
    ) -> None:
        self._id = id
        self._product_id = product_id
        self._quantity = quantity
        self._unit_price = unit_price
        self._status = status
        self._created_at = created_at

    @classmethod
    def place(
        cls,
        *,
        product_id: int,
        quantity: Quantity,
        unit_price: int,
        now: datetime,
    ) -> Order:
        """주문을 생성한다(도메인 팩토리).

        수량 불변식은 Quantity VO 가, 상태·시각은 이 팩토리가 결정한다.
        총액은 unit_price * quantity 로 파생된다(아래 total_price).
        """
        return cls(
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            status=OrderStatus.PLACED,
            created_at=now,
        )

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def product_id(self) -> int:
        return self._product_id

    @property
    def quantity(self) -> Quantity:
        return self._quantity

    @property
    def unit_price(self) -> int:
        return self._unit_price

    @property
    def total_price(self) -> int:
        """주문 시점 단가 스냅샷 * 수량의 파생값(Order 소유)."""
        return self._unit_price * self._quantity.value

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def assign_id(self, id: int) -> None:
        """영속화 후 DB 가 부여한 식별자를 기록한다(리포지토리 전용)."""
        self._id = id
