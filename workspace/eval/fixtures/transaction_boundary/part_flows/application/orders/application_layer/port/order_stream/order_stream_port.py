from __future__ import annotations

from abc import ABC, abstractmethod


class OrderStreamPort(ABC):
    @abstractmethod
    def publish_item(self, order_id: str) -> None: ...
