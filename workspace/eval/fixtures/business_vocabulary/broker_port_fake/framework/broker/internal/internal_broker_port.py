from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable


class InternalBrokerPort(ABC):
    @abstractmethod
    def publish(self, fact: object) -> None: ...

    @abstractmethod
    def subscribe(self, fact_type: type, listener: Callable[[object], None]) -> None: ...
