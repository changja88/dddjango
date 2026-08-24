from __future__ import annotations

from application.orders.domain_layer.drawer.event.drawer_moved import DrawerMoved


class Drawer:
    def __init__(self, drawer_id: str) -> None:
        self.drawer_id: str = drawer_id
        self._events: list = []

    def move(self) -> None:
        self._events.append(DrawerMoved())

    def pull_events(self) -> list:
        drained: list = list(self._events)
        self._events.clear()
        return drained
