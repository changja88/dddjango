from __future__ import annotations

from decimal import Decimal
from typing import TypedDict


class OrderLine(TypedDict):
    quantity: int
    unit_price: Decimal


def create_order_summary(lines: list[OrderLine]) -> dict[str, object]:
    total = sum((line["quantity"] * line["unit_price"] for line in lines), start=Decimal("0"))
    return {
        "total": total,
        "line_count": len(lines),
    }
