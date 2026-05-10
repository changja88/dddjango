from __future__ import annotations

from apps.orders.models import Order


def order_detail_context(order: Order) -> dict[str, object]:
    return {"order": order, "status_label": order.status.value.title()}
