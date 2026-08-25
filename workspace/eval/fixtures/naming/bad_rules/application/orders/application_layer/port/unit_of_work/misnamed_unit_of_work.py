from __future__ import annotations

from abc import ABC, abstractmethod


class ImportOrdersUnitOfWork(ABC):
    """BC명이 접두가 아니다 — #247."""

    @abstractmethod
    def after_commit(self, callback: object) -> None: ...


class OrdersImportUow(ABC):
    """축약 — 판정 ①이 전수 판정으로 가시화한 위반(#247)."""

    @abstractmethod
    def after_commit(self, callback: object) -> None: ...


class OrdersUnitOfWorkImport(ABC):
    """UnitOfWork 가 접미가 아니다 — #247."""

    @abstractmethod
    def after_commit(self, callback: object) -> None: ...
