from __future__ import annotations

from abc import ABC, abstractmethod


class ExtraPort(ABC):
    @abstractmethod
    def poke(self) -> None: ...
