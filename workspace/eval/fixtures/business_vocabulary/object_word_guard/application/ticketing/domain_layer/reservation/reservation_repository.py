from __future__ import annotations

from abc import ABC, abstractmethod

from application.ticketing.domain_layer.reservation.reservation import Reservation


class ReservationRepository(ABC):
    @abstractmethod
    def get(self, reservation_id: str) -> Reservation: ...

    @abstractmethod
    def save(self, reservation: Reservation) -> None: ...
