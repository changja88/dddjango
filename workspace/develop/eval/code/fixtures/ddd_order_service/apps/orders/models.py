from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class OrderStatus(str, Enum):
    DRAFT = "draft"
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass
class Order:
    customer_id: str
    items: list[str]
    id: str = field(default_factory=lambda: str(uuid4()))
    status: OrderStatus = OrderStatus.DRAFT
