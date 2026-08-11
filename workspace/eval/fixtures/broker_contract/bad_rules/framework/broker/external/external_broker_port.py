from __future__ import annotations

from abc import ABC, abstractmethod

from framework.broker.internal.internal_broker_port import InternalBrokerPort


class ExternalBrokerPort(ABC):
    @abstractmethod
    def publish(self, topic: str, payload: str) -> None: ...
