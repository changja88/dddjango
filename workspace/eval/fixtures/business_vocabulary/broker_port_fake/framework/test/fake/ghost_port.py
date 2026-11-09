from __future__ import annotations

from collections.abc import Callable

from framework.broker.internal.internal_broker_port import InternalBrokerPort


class GhostFake(InternalBrokerPort):
    def publish(self, fact: object) -> None:
        return None

    def subscribe(self, fact_type: type, listener: Callable[[object], None]) -> None:
        del fact_type, listener
