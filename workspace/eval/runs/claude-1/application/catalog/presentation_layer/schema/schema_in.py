"""요청 본문 파싱·검증 → PlaceOrderCommand (§2.2 / §2.5).

검증 책임은 표현 계층에 둔다(§5.2) — 도메인·DB에 도달하기 전에 입력 형식을 거른다.
두 분기를 구분한다:
- JSON 자체가 파싱 불가(깨진 본문·객체 아님): 필드를 특정할 수 없으므로 JsonParseError.
- JSON은 파싱됐으나 필드가 누락·비정수·범위 위반(I3: quantity>=1 정수): ValidationError(errors 맵).
"""
import json
from typing import Any, Dict

from application.catalog.application_layer.place_order.dto.place_order_command import (
    PlaceOrderCommand,
)


class JsonParseError(Exception):
    """본문을 JSON 객체로 파싱하지 못한 경우(필드 특정 불가 → errors 생략)."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class ValidationError(Exception):
    """필드 단위 검증 실패(필드명→사유 맵)."""

    def __init__(self, errors: Dict[str, str]) -> None:
        super().__init__("Request validation failed.")
        self.errors = errors


def parse_place_order(raw_body: bytes) -> PlaceOrderCommand:
    """요청 바디(bytes)를 검증해 PlaceOrderCommand로 변환한다.

    파싱 실패는 JsonParseError, 필드 검증 실패는 ValidationError를 던진다(표현 계층이 400으로 변환).
    """
    payload = _parse_json_object(raw_body)

    errors: Dict[str, str] = {}
    product_id = _validate_product_id(payload, errors)
    quantity = _validate_quantity(payload, errors)

    if errors:
        raise ValidationError(errors)

    return PlaceOrderCommand(product_id=product_id, quantity=quantity)


def _parse_json_object(raw_body: bytes) -> Dict[str, Any]:
    """본문을 JSON 객체(dict)로 파싱한다. 실패·비객체는 JsonParseError."""
    try:
        payload = json.loads(raw_body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise JsonParseError("Request body is not valid JSON.")
    if not isinstance(payload, dict):
        raise JsonParseError("Request body must be a JSON object.")
    return payload


def _validate_product_id(payload: Dict[str, Any], errors: Dict[str, str]) -> int:
    """product_id: 필수·정수. 실패 시 errors에 사유를 기록하고 0을 반환한다."""
    if "product_id" not in payload:
        errors["product_id"] = "this field is required"
        return 0
    value = payload["product_id"]
    if not _is_int(value):
        errors["product_id"] = "must be an integer"
        return 0
    return value


def _validate_quantity(payload: Dict[str, Any], errors: Dict[str, str]) -> int:
    """quantity: 필수·정수·>=1(I3). 실패 시 errors에 사유를 기록하고 0을 반환한다."""
    if "quantity" not in payload:
        errors["quantity"] = "this field is required"
        return 0
    value = payload["quantity"]
    if not _is_int(value) or value < 1:
        errors["quantity"] = "must be an integer >= 1"
        return 0
    return value


def _is_int(value: Any) -> bool:
    """JSON 정수 여부. bool 은 int 서브타입이라 명시적으로 배제한다."""
    return isinstance(value, int) and not isinstance(value, bool)
