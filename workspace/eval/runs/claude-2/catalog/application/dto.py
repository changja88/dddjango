"""응용 서비스 입출력 DTO(설계 명세 section 4, 5.3)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrderCommand:
    product_id: int
    quantity: int


@dataclass(frozen=True)
class CreateOrderResult:
    order_id: int
    product_id: int
    quantity: int
    status: str
    remaining_stock: int
