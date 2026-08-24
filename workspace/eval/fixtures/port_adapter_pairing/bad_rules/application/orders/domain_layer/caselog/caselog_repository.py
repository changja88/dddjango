from __future__ import annotations

from abc import ABC, abstractmethod


class CaselogRepository(ABC):
    @abstractmethod
    def get(self, caselog_id: str) -> object: ...

    @abstractmethod
    def save(self, caselog: object) -> None: ...
