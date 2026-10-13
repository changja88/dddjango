from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable


class InternalBrokerPort(ABC):
    @abstractmethod
    def subscribe(self, fact_name: str, listener: Callable) -> None: ...

    @abstractmethod
    def publish(self, fact_name: str, payload: object) -> None: ...
