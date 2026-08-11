from __future__ import annotations

from dataclasses import dataclass

from application.orders.domain_layer.order.order import Order


@dataclass(frozen=True)
class ReduceOrder:
    order: Order

    def as_dict(self) -> dict:
        return {}


@dataclass(frozen=True)
class OrderShipment:
    order_id: str
