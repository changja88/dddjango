from __future__ import annotations

from dataclasses import dataclass

from application.orders.application_layer.order.place_order.place_order_command import PlaceOrderCommand
from application.orders.domain_layer.order.order import Order


@dataclass(frozen=True)
class NoticeIn:
    body: str
    kind: str


@dataclass(frozen=True)
class NoteDto:
    body: str
    kind: str


@dataclass(frozen=True)
class TinyOut:
    code: str
