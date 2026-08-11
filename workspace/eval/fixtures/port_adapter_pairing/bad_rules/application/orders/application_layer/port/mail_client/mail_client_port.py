from __future__ import annotations

from abc import ABC, abstractmethod


class MailClientPort(ABC):
    @abstractmethod
    def send(self, body: str) -> None: ...
