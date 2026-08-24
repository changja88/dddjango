from __future__ import annotations

from application.orders.domain_layer.caselog.event.caselog_moved import CaselogMoved


class Caselog:
    def __init__(self, caselog_id: str) -> None:
        self.caselog_id: str = caselog_id
        self._events: list = []

    def move(self) -> None:
        self._events.append(CaselogMoved())

    def pull_events(self) -> list:
        drained: list = list(self._events)
        self._events.clear()
        return drained
