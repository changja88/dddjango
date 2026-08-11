from __future__ import annotations

from application.orders.domain_layer.order.order import Order
from dataclasses import dataclass


@dataclass(frozen=True)
class Percent:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("퍼센트")
