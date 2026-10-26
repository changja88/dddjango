from __future__ import annotations

from abc import ABC, abstractmethod


class TrayRepository(ABC):
    @abstractmethod
    def get(self, tray_id: str) -> object: ...

    @abstractmethod
    def save(self, tray: object) -> None: ...
