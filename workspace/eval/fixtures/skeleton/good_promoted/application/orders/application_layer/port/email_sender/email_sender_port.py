from __future__ import annotations

from abc import ABC, abstractmethod


class EmailSenderPort(ABC):
    @abstractmethod
    def send(self, notice: object) -> None: ...
