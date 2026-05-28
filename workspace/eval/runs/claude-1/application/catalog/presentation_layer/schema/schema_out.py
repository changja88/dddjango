"""성공(201) 응답 본문 구성(§2.4).

도메인 엔티티를 직접 직렬화하지 않고 표현 계층 dict로 구성한다(Published Language).
status는 표현 계약상 고정 리터럴 "CREATED"로 여기서 채운다(도메인 Order는 status를 모른다 §1.3).
"""
from typing import Any, Dict

from application.catalog.application_layer.place_order.dto.place_order_result import (
    PlaceOrderResult,
)


def order_created_body(result: PlaceOrderResult) -> Dict[str, Any]:
    return {
        "id": result.id,
        "product_id": result.product_id,
        "quantity": result.quantity,
        "unit_price": result.unit_price,
        "total_price": result.total_price,
        "status": "CREATED",
    }
