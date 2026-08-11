from __future__ import annotations

from abc import ABC, abstractmethod


class OrderUnitOfWork(ABC):
    @abstractmethod
    def after_commit(self, callback: object) -> None: ...
