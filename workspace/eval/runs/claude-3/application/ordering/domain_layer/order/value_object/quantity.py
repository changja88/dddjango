"""Quantity 값 객체 (명세 §1.1).

수량 불변식의 정본(canonical)이다 — 요청 스키마 검증·DB CHECK 는 같은
불변식의 방어선일 뿐 판정 정본이 아니다(명세 §1.1 ddd minor m3).
"""
from dataclasses import dataclass

from application.ordering.domain_layer.order.exception import InvalidQuantity


@dataclass(frozen=True)
class Quantity:
    """주문 수량. 1 이상의 정수(불변)."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 1:
            raise InvalidQuantity(f"수량은 1 이상이어야 한다: {self.value}")
