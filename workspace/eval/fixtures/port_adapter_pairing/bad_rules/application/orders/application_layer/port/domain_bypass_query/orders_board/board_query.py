from __future__ import annotations

from abc import ABC, abstractmethod


class OrderBoardQuery(ABC):
    @abstractmethod
    def rows(self) -> "QuerySet":  # noqa: F821
        ...
