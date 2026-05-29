"""주문 생성 성공(201) 응답 스키마 (명세 §2.2).

도메인 Order 를 직접 직렬화하지 않는다 — 응용 서비스 결과 DTO 에서 매핑한다.
"""
from datetime import datetime

from ninja import Schema


class PlaceOrderOut(Schema):
    order_id: int
    product_id: int
    quantity: int
    unit_price: int
    total_price: int
    status: str
    created_at: datetime
