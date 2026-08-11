from __future__ import annotations

from abc import ABC, abstractmethod

from ninja import Schema


class OrderNoticePort(ABC):
    @abstractmethod
    def send_order_notice(self, order_total: int) -> bool: ...

    @abstractmethod
    def render(self, kind: str = "plain") -> str: ...
