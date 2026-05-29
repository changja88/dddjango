"""주문 생성 요청 스키마 (명세 §2.2).

요청 검증의 1차 방어선이다(수량 불변식 정본은 Quantity VO — 명세 §1.1).
product_id·quantity 모두 1 이상의 정수.
"""
from ninja import Schema
from pydantic import Field


class PlaceOrderIn(Schema):
    product_id: int = Field(ge=1)
    quantity: int = Field(ge=1)
