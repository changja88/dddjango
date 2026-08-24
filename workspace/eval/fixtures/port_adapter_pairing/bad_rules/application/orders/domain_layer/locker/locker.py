from __future__ import annotations

from application.orders.domain_layer.locker.event.locker_moved import LockerMoved


class Locker:
    def __init__(self, locker_id: str) -> None:
        self.locker_id: str = locker_id
        self._pending_events: list = []

    def move(self) -> None:
        self._pending_events.append(LockerMoved())

    @property
    def pending_events(self) -> tuple:
        return tuple(self._pending_events)

    @property
    def has_pending(self) -> bool:
        return False

    def pull_events(self) -> tuple:
        drained: tuple = tuple(self._pending_events)
        self._pending_events.clear()
        return drained
