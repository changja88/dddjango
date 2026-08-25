from __future__ import annotations

from abc import ABC, abstractmethod


class OrdersLedgerUnitOfWork(ABC):
    """open/close 수동 방식 + __enter__/__exit__ 부재 — #245(판정 ② missing-each·extra)."""

    @abstractmethod
    def open(self) -> None: ...

    @abstractmethod
    def close(self, exception: object) -> None: ...

    @abstractmethod
    def after_commit(self, callback: object) -> None: ...


class OrdersBinUnitOfWork(ABC):
    """여분 dunder(__call__) — 종전 불가시, exact-set 이 잡는다(#245)."""

    @abstractmethod
    def __enter__(self) -> "OrdersBinUnitOfWork": ...

    @abstractmethod
    def __exit__(self, exc_type: object, exc: object, tb: object) -> None: ...

    @abstractmethod
    def __call__(self) -> None: ...

    @abstractmethod
    def after_commit(self, callback: object) -> None: ...
