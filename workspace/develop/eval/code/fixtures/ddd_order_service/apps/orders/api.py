from __future__ import annotations

from apps.orders.models import Order
from apps.orders.services import place_order


def create_order(customer_id: str, items: list[str]) -> Order:
    return place_order(customer_id, items)
