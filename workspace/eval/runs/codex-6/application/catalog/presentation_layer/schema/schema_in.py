import json
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Optional


class ReservationRequestValidationError(Exception):
    def __init__(
        self,
        detail: str,
        errors: Optional[list[dict[str, str]]] = None,
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.errors = errors or []


@dataclass(frozen=True)
class ReserveProductStockRequest:
    quantity: int


def parse_reserve_product_stock_request(body: bytes) -> ReserveProductStockRequest:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, JSONDecodeError) as exc:
        raise ReservationRequestValidationError(
            detail="Request body must be valid JSON.",
            errors=[{"field": "body", "message": "Must be valid JSON."}],
        ) from exc

    if not isinstance(payload, dict):
        raise ReservationRequestValidationError(
            detail="Request body must be a JSON object.",
            errors=[{"field": "body", "message": "Must be a JSON object."}],
        )

    if "quantity" not in payload:
        raise ReservationRequestValidationError(
            detail="quantity is required.",
            errors=[{"field": "quantity", "message": "This field is required."}],
        )

    quantity = payload["quantity"]
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ReservationRequestValidationError(
            detail="quantity must be an integer.",
            errors=[{"field": "quantity", "message": "Must be an integer."}],
        )

    if quantity <= 0:
        raise ReservationRequestValidationError(
            detail="quantity must be positive.",
            errors=[{"field": "quantity", "message": "Must be positive."}],
        )

    return ReserveProductStockRequest(quantity=quantity)
