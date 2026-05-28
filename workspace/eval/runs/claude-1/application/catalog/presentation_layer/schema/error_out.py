"""에러 응답 본문 — RFC 9457 Problem Details 구성(§2.5).

Content-Type 'application/problem+json'. 공통 필드 type/title/status/detail + 상황별 확장 필드.
type은 전용 URI 미운영이라 about:blank.
"""
from typing import Any, Dict


def insufficient_stock(
    product_id: int, available_stock: int, requested_quantity: int
) -> Dict[str, Any]:
    return {
        "type": "about:blank",
        "title": "Insufficient stock",
        "status": 409,
        "detail": (
            f"Product {product_id} has stock {available_stock} "
            f"but {requested_quantity} was requested."
        ),
        "product_id": product_id,
        "available_stock": available_stock,
        "requested_quantity": requested_quantity,
    }


def product_not_found(product_id: int) -> Dict[str, Any]:
    return {
        "type": "about:blank",
        "title": "Product not found",
        "status": 404,
        "detail": f"Product {product_id} not found.",
        "product_id": product_id,
    }


def invalid_request(errors: Dict[str, str]) -> Dict[str, Any]:
    """입력 검증 실패(400) — 필드명→사유 맵을 errors에 담는다(§2.5)."""
    return {
        "type": "about:blank",
        "title": "Invalid request",
        "status": 400,
        "detail": "Request validation failed.",
        "errors": errors,
    }


def invalid_json(detail: str) -> Dict[str, Any]:
    """JSON 파싱 실패(400) — 필드 특정 불가라 errors를 생략하고 detail만 담는다(§2.5)."""
    return {
        "type": "about:blank",
        "title": "Invalid request",
        "status": 400,
        "detail": detail,
    }


def method_not_allowed() -> Dict[str, Any]:
    """허용되지 않은 메서드(405) — Problem Details(§2.5). Allow 헤더는 뷰가 부여한다."""
    return {
        "type": "about:blank",
        "title": "Method not allowed",
        "status": 405,
        "detail": "Only POST is allowed on this endpoint.",
    }
