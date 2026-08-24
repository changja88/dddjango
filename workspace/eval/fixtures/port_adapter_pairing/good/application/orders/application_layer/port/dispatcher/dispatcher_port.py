from __future__ import annotations

from abc import ABC, abstractmethod


class DispatcherPort(ABC):
    @abstractmethod
    def send_notice(self, payload: str) -> None: ...
