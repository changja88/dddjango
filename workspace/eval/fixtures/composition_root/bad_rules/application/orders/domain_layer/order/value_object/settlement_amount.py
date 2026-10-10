from __future__ import annotations

from dataclasses import dataclass
from decimal import getcontext as Context

from application.orders.domain_layer.order.exception.invalid_settlement_amount import (
    InvalidSettlementAmount,
)


@dataclass(frozen=True, slots=True)
class SettlementAmount:
    """정산 금액이다 — 이 모듈이 들인 예외 이름과 `Context` 는 값 객체가 아니다(r3)."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidSettlementAmount
