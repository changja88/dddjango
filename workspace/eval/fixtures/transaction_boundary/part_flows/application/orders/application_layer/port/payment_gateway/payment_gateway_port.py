from __future__ import annotations

from abc import ABC, abstractmethod


class PaymentGatewayPort(ABC):
    @abstractmethod
    def reserve(self, order_id: str, amount: int) -> None: ...
