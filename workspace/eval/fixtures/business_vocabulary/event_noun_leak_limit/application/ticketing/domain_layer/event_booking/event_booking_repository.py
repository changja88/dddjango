from __future__ import annotations

from abc import ABC, abstractmethod

from application.ticketing.domain_layer.event_booking.event_booking import EventBooking


class EventBookingRepository(ABC):
    @abstractmethod
    def get(self, event_booking_id: str) -> EventBooking: ...

    @abstractmethod
    def save(self, event_booking: EventBooking) -> None: ...
