from __future__ import annotations

from abc import ABC, abstractmethod


class MailPort(ABC):
    @abstractmethod
    def notify(self) -> None: ...

    @abstractmethod
    def transmit_payload(self, body: str) -> None: ...

    @abstractmethod
    def commit(self) -> None: ...

    def plain_send(self, body: str) -> None:
        return None


class ExtraMailPort:
    def poke(self) -> None:
        return None
