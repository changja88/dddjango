from __future__ import annotations

from decimal import Decimal

from ninja import NinjaAPI, Schema

from .services import IdempotencyConflict, order_create


api = NinjaAPI(title="dddjango Eval Shop Service")


class OrderCreateIn(Schema):
    customer_email: str
    total_amount: Decimal
    note: str = ""


class OrderOut(Schema):
    id: int
    customer_email: str
    total_amount: str
    status: str
    replayed: bool


class ErrorOut(Schema):
    detail: str


@api.post("/orders", response={200: OrderOut, 201: OrderOut, 409: ErrorOut})
def create_order(request, payload: OrderCreateIn):
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        return 409, {"detail": "Idempotency-Key header is required"}
    try:
        result = order_create(
            idempotency_key=idempotency_key,
            customer_email=payload.customer_email,
            total_amount=payload.total_amount,
            note=payload.note,
        )
    except IdempotencyConflict as exc:
        return 409, {"detail": str(exc)}

    order = result.order
    status_code = 200 if result.replayed else 201
    return status_code, {
        "id": order.id,
        "customer_email": order.customer_email,
        "total_amount": str(order.total_amount),
        "status": order.status,
        "replayed": result.replayed,
    }
