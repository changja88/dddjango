from __future__ import annotations

from decimal import Decimal
from typing import TypedDict


class OrderLine(TypedDict):
    quantity: int
    unit_price: Decimal


def create_order_summary(lines: list[OrderLine]) -> dict[str, object]:
    raise NotImplementedError("Implement order summary calculation.")
