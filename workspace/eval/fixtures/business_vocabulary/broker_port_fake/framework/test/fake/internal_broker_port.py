from __future__ import annotations

from collections.abc import Callable

from framework.broker.internal.internal_broker_port import InternalBrokerPort


class InternalBrokerFake(InternalBrokerPort):
    def __init__(self) -> None:
        self.published: list[object] = []

    def publish(self, fact: object) -> None:
        self.published.append(fact)

    def subscribe(self, fact_type: type, listener: Callable[[object], None]) -> None:
        del fact_type, listener
