from __future__ import annotations

from abc import ABC, abstractmethod


class PaymentGatewayPort(ABC):
    @abstractmethod
    def charge(self, order_id: str) -> None: ...
