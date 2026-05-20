#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("eval_code_behavior_checks.py")


def load_checker():
    spec = importlib.util.spec_from_file_location("eval_code_behavior_checks", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReservationBehaviorCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.checker = load_checker()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name)
        self.write_package("apps")
        self.write_package("apps/reservations")

    def write_package(self, relative: str) -> None:
        package = self.workspace / relative
        package.mkdir(parents=True, exist_ok=True)
        (package / "__init__.py").write_text("", encoding="utf-8")

    def write_file(self, relative: str, text: str) -> None:
        path = self.workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")

    def write_reservation_model(self, *, public_status: bool) -> None:
        if public_status:
            self.write_file(
                "apps/reservations/models.py",
                """
                from __future__ import annotations

                from dataclasses import dataclass, field
                from enum import Enum
                from uuid import uuid4

                class ReservationStatus(str, Enum):
                    REQUESTED = "requested"
                    CONFIRMED = "confirmed"
                    EXPIRED = "expired"

                class ReservationRuleViolation(ValueError):
                    pass

                @dataclass
                class Reservation:
                    customer_id: str
                    room_id: str
                    nights: int
                    id: str = field(default_factory=lambda: str(uuid4()))
                    status: ReservationStatus = ReservationStatus.REQUESTED

                    @classmethod
                    def request(cls, customer_id: str, room_id: str, nights: int) -> Reservation:
                        if nights < 1:
                            raise ReservationRuleViolation("reservation must be for at least one night")
                        return cls(customer_id=customer_id, room_id=room_id, nights=nights)

                    def confirm(self) -> None:
                        if self.status is not ReservationStatus.REQUESTED:
                            raise ReservationRuleViolation("only requested reservations can be confirmed")
                        self.status = ReservationStatus.CONFIRMED

                    def expire(self) -> None:
                        if self.status is ReservationStatus.CONFIRMED:
                            raise ReservationRuleViolation("confirmed reservations cannot expire")
                        if self.status is not ReservationStatus.REQUESTED:
                            raise ReservationRuleViolation("only requested reservations can expire")
                        self.status = ReservationStatus.EXPIRED
                """,
            )
            return

        self.write_file(
            "apps/reservations/models.py",
            """
            from __future__ import annotations

            from dataclasses import dataclass, field
            from enum import Enum
            from uuid import uuid4

            class ReservationStatus(str, Enum):
                REQUESTED = "requested"
                CONFIRMED = "confirmed"
                EXPIRED = "expired"

            class ReservationRuleViolation(ValueError):
                pass

            @dataclass
            class Reservation:
                customer_id: str
                room_id: str
                nights: int
                id: str = field(default_factory=lambda: str(uuid4()))
                _status: ReservationStatus = field(default=ReservationStatus.REQUESTED, init=False, repr=False)

                @classmethod
                def request(cls, customer_id: str, room_id: str, nights: int) -> Reservation:
                    if nights < 1:
                        raise ReservationRuleViolation("reservation must be for at least one night")
                    return cls(customer_id=customer_id, room_id=room_id, nights=nights)

                @property
                def status(self) -> ReservationStatus:
                    return self._status

                def confirm(self) -> None:
                    if self._status is not ReservationStatus.REQUESTED:
                        raise ReservationRuleViolation("only requested reservations can be confirmed")
                    self._status = ReservationStatus.CONFIRMED

                def expire(self) -> None:
                    if self._status is ReservationStatus.CONFIRMED:
                        raise ReservationRuleViolation("confirmed reservations cannot expire")
                    if self._status is not ReservationStatus.REQUESTED:
                        raise ReservationRuleViolation("only requested reservations can expire")
                    self._status = ReservationStatus.EXPIRED
            """,
        )

    def write_service(self, *, direct_setattr: bool = False) -> None:
        confirm_body = (
            'setattr(reservation, "status", ReservationStatus.CONFIRMED)\n'
            "                return reservation"
            if direct_setattr
            else "reservation.confirm()\n"
            "                return reservation"
        )
        self.write_file(
            "apps/reservations/services.py",
            f"""
            from __future__ import annotations

            from dataclasses import dataclass, field

            from apps.reservations.models import Reservation, ReservationStatus

            _RESERVATIONS: dict[str, Reservation] = {{}}

            @dataclass
            class InMemoryRoomAvailabilityBoundary:
                held_room_ids: set[str] = field(default_factory=set)

                def hold_requested_reservation(self, reservation: Reservation) -> None:
                    self.held_room_ids.add(reservation.room_id)

                def release_expired_reservation(self, reservation: Reservation) -> None:
                    self.held_room_ids.discard(reservation.room_id)

            _ROOM_AVAILABILITY = InMemoryRoomAvailabilityBoundary()

            def request_reservation(customer_id: str, room_id: str, nights: int) -> Reservation:
                reservation = Reservation.request(customer_id, room_id, nights)
                _ROOM_AVAILABILITY.hold_requested_reservation(reservation)
                _RESERVATIONS[reservation.id] = reservation
                return reservation

            def confirm_reservation(reservation_id: str) -> Reservation:
                reservation = _RESERVATIONS[reservation_id]
                {confirm_body}

            def expire_reservation(reservation_id: str) -> Reservation:
                reservation = _RESERVATIONS[reservation_id]
                reservation.expire()
                _ROOM_AVAILABILITY.release_expired_reservation(reservation)
                return reservation
            """,
        )

    def test_reservation_public_status_field_fails_boundary_check(self) -> None:
        self.write_reservation_model(public_status=True)
        self.write_service()

        with self.assertRaisesRegex(AssertionError, "externally mutable"):
            self.checker.run_ddd_reservation_boundary(self.workspace)

    def test_reservation_private_read_only_status_passes_boundary_check(self) -> None:
        self.write_reservation_model(public_status=False)
        self.write_service()

        self.checker.run_ddd_reservation_boundary(self.workspace)

    def test_service_setattr_status_mutation_fails_boundary_check(self) -> None:
        self.write_reservation_model(public_status=True)
        self.write_service(direct_setattr=True)

        with self.assertRaisesRegex(AssertionError, "application service"):
            self.checker.run_ddd_reservation_boundary(self.workspace)


if __name__ == "__main__":
    unittest.main()
