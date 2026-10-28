from __future__ import annotations

from abc import ABC, abstractmethod


class OrdersUnitOfWork(ABC):
    @abstractmethod
    def __enter__(self) -> "OrdersUnitOfWork": ...

    @abstractmethod
    def __exit__(self, exc_type: object, exc: object, tb: object) -> None: ...

    @abstractmethod
    def after_commit(self, callback: object) -> None: ...
