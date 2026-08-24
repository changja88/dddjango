from __future__ import annotations

from application.orders.domain_layer.gauge.event.gauge_read import GaugeRead


class Gauge:
    def __init__(self, gauge_id: str) -> None:
        self.gauge_id: str = gauge_id
        self._events: list = []

    def read(self, value: int) -> None:
        self._value: int = value
        self._events.append(GaugeRead())

    def pull_events(self) -> list:
        drained: list = list(self._events)
        self._events.clear()
        return drained
