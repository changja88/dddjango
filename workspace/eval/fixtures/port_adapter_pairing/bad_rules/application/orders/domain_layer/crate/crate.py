from __future__ import annotations

from application.orders.domain_layer.crate.event.crate_moved import CrateMoved


class Crate:
    def __init__(self, crate_id: str) -> None:
        self.crate_id: str = crate_id
        self._events: list = []

    def move(self) -> None:
        self._events.append(CrateMoved())

    def pull_events(self) -> list:
        drained: list = list(self._events)
        self._events.clear()
        return drained
