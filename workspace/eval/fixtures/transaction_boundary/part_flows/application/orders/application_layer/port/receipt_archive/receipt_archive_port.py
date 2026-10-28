from __future__ import annotations

from abc import ABC, abstractmethod


class ReceiptArchivePort(ABC):
    @abstractmethod
    def save_record(self, order_id: str) -> None: ...
