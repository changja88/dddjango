from __future__ import annotations

from abc import ABC, abstractmethod


class BoxRepository(ABC):
    @abstractmethod
    def get(self, box_id: str) -> object: ...

    @abstractmethod
    def save(self, box: object) -> None: ...
