from __future__ import annotations

from abc import ABC, abstractmethod


class LedgerLoadPort(ABC):
    @abstractmethod
    def load_rows(self, batch: tuple[str, ...]) -> int: ...
