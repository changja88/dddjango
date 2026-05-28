"""PlaceOrderResult — 주문 생성 유스케이스 출력 DTO.

표현 계층 schema_out이 응답을 구성하는 데 필요한 표시 값만 담는다(도메인 직접 노출 금지 §2.4).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceOrderResult:
    id: int
    product_id: int
    quantity: int
    unit_price: int
    total_price: int
