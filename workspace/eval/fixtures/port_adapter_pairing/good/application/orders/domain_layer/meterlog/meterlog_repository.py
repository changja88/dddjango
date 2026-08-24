from __future__ import annotations

from abc import ABC, abstractmethod


class MeterlogRepository(ABC):
    @abstractmethod
    def get(self, meterlog_id: str) -> object: ...

    @abstractmethod
    def save(self, meterlog: object) -> None: ...
