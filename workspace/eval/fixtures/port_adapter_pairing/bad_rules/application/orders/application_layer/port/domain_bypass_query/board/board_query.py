from __future__ import annotations

from abc import ABC, abstractmethod


class BoardDomainBypassQuery(ABC):
    @abstractmethod
    def fetch(self) -> list: ...
