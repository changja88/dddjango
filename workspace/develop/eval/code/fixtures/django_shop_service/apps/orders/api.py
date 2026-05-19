from __future__ import annotations

from decimal import Decimal

from ninja import NinjaAPI, Schema

from .services import order_create


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


@api.post("/orders", response={201: OrderOut, 409: ErrorOut})
def create_order(request, payload: OrderCreateIn):
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        return 409, {"detail": "Idempotency-Key header is required"}
    result = order_create(
        idempotency_key=idempotency_key,
        customer_email=payload.customer_email,
        total_amount=payload.total_amount,
        note=payload.note,
    )

    order = result.order
    return 201, {
        "id": order.id,
        "customer_email": order.customer_email,
        "total_amount": str(order.total_amount),
        "status": order.status,
        "replayed": result.replayed,
    }
