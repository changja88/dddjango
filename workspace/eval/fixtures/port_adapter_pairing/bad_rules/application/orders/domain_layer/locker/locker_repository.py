from __future__ import annotations

from abc import ABC, abstractmethod


class LockerRepository(ABC):
    @abstractmethod
    def get(self, locker_id: str) -> object: ...

    @abstractmethod
    def save(self, locker: object) -> None: ...
