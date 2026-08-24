from __future__ import annotations

from abc import ABC, abstractmethod


class MeterRepository(ABC):
    @abstractmethod
    def get(self, meter_id: str) -> object: ...

    @abstractmethod
    def save(self, meter: object) -> None: ...
