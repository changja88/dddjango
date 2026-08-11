from __future__ import annotations

from abc import ABC, abstractmethod


class OrderBoardDomainBypassQuery(ABC):
    @abstractmethod
    def count_open(self) -> int: ...
