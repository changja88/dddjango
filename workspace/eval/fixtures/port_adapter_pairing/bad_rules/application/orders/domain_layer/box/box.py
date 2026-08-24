from __future__ import annotations

from application.orders.domain_layer.box.event.box_moved import BoxMoved


class Box:
    def __init__(self, box_id: str) -> None:
        self.box_id: str = box_id
        self._events: list = []

    def move(self) -> None:
        self._events.append(BoxMoved())

    def pull_events(self) -> list:
        drained: list = list(self._events)
        self._events.clear()
        return drained
