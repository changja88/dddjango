"""주문 생성 결과 DTO (명세 §2.2 — 도메인 직접 직렬화 금지).

응용 서비스가 표현 계층에 돌려주는 출력 경계 DTO다. 도메인 Order 애그리거트를
표현 계층에 직접 노출하지 않고, 표현이 필요로 하는 표시 값만 담는다.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PlaceOrderResult:
    order_id: int
    product_id: int
    quantity: int
    unit_price: int
    total_price: int
    status: str
    created_at: datetime
