from typing import Any, Dict

from application.catalog.application_layer.create_order.dto.create_order_command import (
    CreateOrderCommand,
)


class InvalidOrderRequest(Exception):
    def __init__(self, errors: Dict[str, list]) -> None:
        super().__init__("Request body is invalid.")
        self.errors = errors


def parse_create_order_command(payload: Any) -> CreateOrderCommand:
    if not isinstance(payload, dict):
        raise InvalidOrderRequest(
            {"non_field_errors": ["Request body must be a JSON object."]}
        )

    errors: Dict[str, list] = {}
    allowed_fields = {"product_id", "quantity"}
    for field in sorted(set(payload) - allowed_fields):
        errors[field] = ["Unknown field."]

    product_id = _positive_integer(payload, "product_id", errors)
    quantity = _positive_integer(payload, "quantity", errors)

    if errors:
        raise InvalidOrderRequest(errors)
    return CreateOrderCommand(product_id=product_id, quantity=quantity)


def _positive_integer(payload: Dict[str, Any], field: str, errors: Dict[str, list]) -> int:
    value = payload.get(field)
    if field not in payload:
        errors[field] = ["This field is required."]
        return 0
    if not isinstance(value, int) or isinstance(value, bool):
        errors[field] = ["This field must be a positive integer."]
        return 0
    if value <= 0:
        errors[field] = ["This field must be a positive integer."]
        return 0
    return value
