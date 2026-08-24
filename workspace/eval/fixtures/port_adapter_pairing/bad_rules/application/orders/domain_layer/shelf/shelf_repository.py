from __future__ import annotations

from abc import ABC, abstractmethod


class ShelfRepository(ABC):
    @abstractmethod
    def get(self, shelf_id: str) -> object: ...

    @abstractmethod
    def save(self, shelf: object) -> None: ...
