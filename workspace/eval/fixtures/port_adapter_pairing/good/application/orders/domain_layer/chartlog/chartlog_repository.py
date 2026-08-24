from __future__ import annotations

from abc import ABC, abstractmethod


class ChartlogRepository(ABC):
    @abstractmethod
    def get(self, chartlog_id: str) -> object: ...

    @abstractmethod
    def save(self, chartlog: object) -> None: ...
