from __future__ import annotations

from dataclasses import dataclass

from application.orders.domain_layer.order.exception.invalid_order_threshold import (
    InvalidOrderThreshold,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class OrderThresholds:
    """주문 경고 금액과 차단 금액의 유효한 조합이다."""

    warning: int
    block: int

    @classmethod
    def create(cls, *, warning: int, block: int) -> OrderThresholds:
        if warning <= 0 or warning >= block:
            raise InvalidOrderThreshold
        return cls(warning=warning, block=block)
