"""PlaceOrderCommand — 주문 생성 유스케이스 입력 DTO.

표현 계층이 검증·파싱을 마친 유효한 입력을 담아 응용에 전달한다(§5.2).
필드 단위 입력 검증(I3)은 표현 계층 schema_in이 수행하므로, 여기는 유효한 값의 전달자다.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceOrderCommand:
    product_id: int
    quantity: int
