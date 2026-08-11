from __future__ import annotations

from abc import ABC, abstractmethod


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: object) -> None: ...
