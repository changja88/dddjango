from __future__ import annotations

from enum import StrEnum


class OrderStatus(StrEnum):
    PLACED = "placed"
    SHIPPED = "shipped"
