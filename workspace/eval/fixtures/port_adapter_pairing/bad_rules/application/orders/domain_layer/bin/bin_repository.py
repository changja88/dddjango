from __future__ import annotations

from abc import ABC, abstractmethod


class BinRepository(ABC):
    @abstractmethod
    def get(self, bin_id: str) -> object: ...

    @abstractmethod
    def save(self, bin: object) -> None: ...
