from __future__ import annotations

from collections.abc import Callable

from framework.broker.internal.internal_broker_port import InternalBrokerPort


class InternalBroker(InternalBrokerPort):
    def __init__(self, failure_sink: Callable) -> None:
        self._table: dict = {}
        self._failure_sink: Callable = failure_sink

    def subscribe(self, fact_name: str, listener: Callable) -> None:
        self._table.setdefault(fact_name, set()).add(listener)

    def publish(self, fact_name: str, payload: object) -> None:
        for listener in self._table.get(fact_name, set()):
            try:
                listener(payload)
            except Exception as exc:
                self._failure_sink(fact_name, exc)


broker_instance: InternalBroker | None = None
