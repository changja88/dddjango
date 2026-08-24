from __future__ import annotations

from abc import ABC, abstractmethod


class GaugeRepository(ABC):
    @abstractmethod
    def get(self, gauge_id: str) -> object: ...

    @abstractmethod
    def save(self, gauge: object) -> None: ...
