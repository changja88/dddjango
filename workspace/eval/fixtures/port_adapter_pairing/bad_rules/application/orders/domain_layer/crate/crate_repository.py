from __future__ import annotations

from abc import ABC, abstractmethod


class CrateRepository(ABC):
    @abstractmethod
    def get(self, crate_id: str) -> object: ...

    @abstractmethod
    def save(self, crate: object) -> None: ...
