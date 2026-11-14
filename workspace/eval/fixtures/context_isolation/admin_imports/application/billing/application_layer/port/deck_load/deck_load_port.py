from __future__ import annotations

from abc import ABC, abstractmethod


class DeckLoadPort(ABC):
    @abstractmethod
    def load_deck(self, rows: tuple[str, ...]) -> int: ...
