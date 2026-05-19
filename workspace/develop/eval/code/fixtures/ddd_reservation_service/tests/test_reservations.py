from __future__ import annotations

import unittest

from apps.reservations.models import ReservationStatus
from apps.reservations.services import (
    _RESERVATIONS,
    _ROOM_HOLDS,
    confirm_reservation,
    expire_reservation,
    request_reservation,
)


class ReservationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        _RESERVATIONS.clear()
        _ROOM_HOLDS.clear()

    def test_request_reservation_moves_to_requested_and_holds_room(self) -> None:
        reservation = request_reservation("customer-1", "room-101", 2)

        self.assertEqual(reservation.status, ReservationStatus.REQUESTED)
        self.assertEqual(_RESERVATIONS[reservation.id], reservation)
        self.assertIn("room-101", _ROOM_HOLDS)

    def test_confirm_reservation_moves_to_confirmed(self) -> None:
        reservation = request_reservation("customer-1", "room-101", 2)

        confirmed = confirm_reservation(reservation.id)

        self.assertEqual(confirmed.status, ReservationStatus.CONFIRMED)

    def test_expire_reservation_releases_room_hold(self) -> None:
        reservation = request_reservation("customer-1", "room-101", 2)

        expired = expire_reservation(reservation.id)

        self.assertEqual(expired.status, ReservationStatus.EXPIRED)
        self.assertNotIn("room-101", _ROOM_HOLDS)


if __name__ == "__main__":
    unittest.main()
