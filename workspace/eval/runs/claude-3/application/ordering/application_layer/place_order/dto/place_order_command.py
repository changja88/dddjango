"""주문 생성 입력 DTO (명세 §4.1).

표현 계층의 요청 스키마와 도메인 사이의 경계 DTO다 — 응용 서비스 입력 계약.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceOrderCommand:
    product_id: int
    quantity: int
