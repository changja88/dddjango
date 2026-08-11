from __future__ import annotations

from abc import ABC, abstractmethod


class LedgerRepository(ABC):
    @abstractmethod
    def save(self, ledger: object) -> None: ...
