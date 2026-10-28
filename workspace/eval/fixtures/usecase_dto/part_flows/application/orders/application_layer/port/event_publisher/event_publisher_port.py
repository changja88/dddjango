from __future__ import annotations

from abc import ABC, abstractmethod


class EventPublisherPort(ABC):
    @abstractmethod
    def publish(self, order_id: str) -> None: ...
