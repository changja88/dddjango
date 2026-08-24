from __future__ import annotations

from application.orders.domain_layer.meterlog.event.meterlog_noted import MeterlogNoted


class Meterlog:
    def __init__(self, meterlog_id: str) -> None:
        self.meterlog_id: str = meterlog_id
        self._events: list = []

    def note(self) -> None:
        self._events.append(MeterlogNoted())

    def pull_events(self) -> list:
        drained: list = list(self._events)
        self._events.clear()
        return drained
