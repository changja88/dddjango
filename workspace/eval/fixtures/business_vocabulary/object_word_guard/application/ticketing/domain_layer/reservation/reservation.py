from __future__ import annotations

from application.ticketing.domain_layer.reservation.event.archived_object import ArchivedObject


class Reservation:
    def __init__(self, reservation_id: str) -> None:
        self.reservation_id: str = reservation_id
        self._events: list = []

    def confirm(self) -> None:
        self._events.append(ArchivedObject(reservation_id=self.reservation_id))
        self._ensure_valid()

    def pull_events(self) -> list:
        drained: list = list(self._events)
        self._events.clear()
        return drained

    def _ensure_valid(self) -> None:
        return None
