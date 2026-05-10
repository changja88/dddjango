from __future__ import annotations

from apps.orders.services import create_order


def create_order_endpoint(payload: dict[str, object]) -> dict[str, object]:
    order = create_order(
        customer_id=str(payload["customer_id"]),
        items=list(payload["items"]),
        memo=str(payload.get("memo", "")),
    )
    return {"id": order.id, "status": order.status.value}
