from __future__ import annotations

from abc import ABC, abstractmethod


class EmailPort(ABC):
    @abstractmethod
    def send(self, notice: "NoticeOut") -> None: ...
