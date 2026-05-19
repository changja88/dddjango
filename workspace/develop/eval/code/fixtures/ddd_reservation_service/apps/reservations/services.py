from __future__ import annotations

from apps.reservations.models import Reservation, ReservationStatus


_RESERVATIONS: dict[str, Reservation] = {}
_ROOM_HOLDS: set[str] = set()


def request_reservation(customer_id: str, room_id: str, nights: int) -> Reservation:
    if nights < 1:
        raise ValueError("nights must be positive")
    reservation = Reservation(customer_id=customer_id, room_id=room_id, nights=nights)
    reservation.status = ReservationStatus.REQUESTED
    _ROOM_HOLDS.add(room_id)
    _RESERVATIONS[reservation.id] = reservation
    return reservation


def confirm_reservation(reservation_id: str) -> Reservation:
    reservation = _RESERVATIONS[reservation_id]
    reservation.status = ReservationStatus.CONFIRMED
    return reservation


def expire_reservation(reservation_id: str) -> Reservation:
    reservation = _RESERVATIONS[reservation_id]
    reservation.status = ReservationStatus.EXPIRED
    _ROOM_HOLDS.discard(reservation.room_id)
    return reservation
