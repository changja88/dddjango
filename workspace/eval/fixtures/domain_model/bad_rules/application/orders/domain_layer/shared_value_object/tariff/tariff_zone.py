from __future__ import annotations

from dataclasses import dataclass

from application.orders.domain_layer.order.order import Order


@dataclass(frozen=True)
class TariffZone:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("요금 지역")
