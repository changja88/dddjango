from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class OrderStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass
class Order:
    customer_id: str
    items: list[str]
    memo: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    status: OrderStatus = OrderStatus.DRAFT

    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise ValueError("only pending orders can be confirmed")
        self.status = OrderStatus.CONFIRMED
