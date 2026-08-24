from __future__ import annotations

from abc import ABC, abstractmethod


class DrawerRepository(ABC):
    @abstractmethod
    def get(self, drawer_id: str) -> object: ...

    @abstractmethod
    def save(self, drawer: object) -> None: ...
