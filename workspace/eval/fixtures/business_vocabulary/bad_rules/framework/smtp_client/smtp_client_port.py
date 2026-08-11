from __future__ import annotations

from abc import ABC, abstractmethod


class SmtpClientPort(ABC):
    @abstractmethod
    def push(self, body: str) -> None: ...
