from __future__ import annotations

from application.orders.domain_layer.chartlog.event.chartlog_noted import ChartlogNoted


class Chartlog:
    def __init__(self, chartlog_id: str) -> None:
        self.chartlog_id: str = chartlog_id
        self._events: list = []

    def note(self) -> None:
        self._events.append(ChartlogNoted())

    def pull_events(self) -> list:
        drained: list = list(self._events)
        self._events.clear()
        return drained
