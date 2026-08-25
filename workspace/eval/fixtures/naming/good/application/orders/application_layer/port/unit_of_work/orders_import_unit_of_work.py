from __future__ import annotations

from abc import ABC, abstractmethod


class OrdersImportUnitOfWork(ABC):
    """역할 수식어(Import)가 붙은 트랜잭션 소유자 — 판정 ① 양성."""

    @abstractmethod
    def __enter__(self) -> "OrdersImportUnitOfWork": ...

    @abstractmethod
    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool: ...

    @abstractmethod
    def after_commit(self, callback: object) -> None: ...
