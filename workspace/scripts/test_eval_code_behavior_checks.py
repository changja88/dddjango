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


class OrderBehaviorCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.checker = load_checker()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name)
        self.write_package("apps")
        self.write_package("apps/orders")

    def write_package(self, relative: str) -> None:
        package = self.workspace / relative
        package.mkdir(parents=True, exist_ok=True)
        (package / "__init__.py").write_text("", encoding="utf-8")

    def write_file(self, relative: str, text: str) -> None:
        path = self.workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")

    def write_order_model(
        self,
        *,
        public_status: bool,
        private_attr: str = "_status",
        guard_private_attr: bool = True,
    ) -> None:
        if public_status:
            status_field = "status: OrderStatus = OrderStatus.DRAFT"
            status_property = ""
            status_reads = "self.status"
            status_writes = "self.status"
            setattr_guard = ""
        else:
            status_field = f"{private_attr}: OrderStatus = field(default=OrderStatus.DRAFT, init=False, repr=False)"
            status_property = """
                @property
                def status(self) -> OrderStatus:
                    return self.{private_attr}
            """
            status_reads = "self._status"
            status_writes = "self._status"
            status_property = status_property.format(private_attr=private_attr)
            status_reads = f"self.{private_attr}"
            status_writes = f"self.{private_attr}"
            if guard_private_attr:
                setattr_guard = f"""
                def __setattr__(self, name: str, value: object) -> None:
                    if name == "{private_attr}" and hasattr(self, "{private_attr}") and not getattr(self, "_changing_status", False):
                        raise AttributeError("status is read-only")
                    super().__setattr__(name, value)

                def _set_status(self, status: OrderStatus) -> None:
                    self._changing_status = True
                    try:
                        self.{private_attr} = status
                    finally:
                        self._changing_status = False
            """
            else:
                setattr_guard = """
                def _set_status(self, status: OrderStatus) -> None:
                    self.{private_attr} = status
            """.format(private_attr=private_attr)
        self.write_file(
            "apps/orders/models.py",
            f"""
            from __future__ import annotations

            from dataclasses import dataclass, field
            from enum import Enum
            from uuid import uuid4

            class OrderStatus(str, Enum):
                DRAFT = "draft"
                PENDING_PAYMENT = "pending_payment"
                CONFIRMED = "confirmed"

            @dataclass
            class Order:
                customer_id: str
                items: list[str]
                id: str = field(default_factory=lambda: str(uuid4()))
                {status_field}
            {status_property}
            {setattr_guard}
                @classmethod
                def place(cls, customer_id: str, items: list[str]) -> Order:
                    if not items:
                        raise ValueError("empty order")
                    order = cls(customer_id=customer_id, items=items)
                    order._mark_pending_payment()
                    return order

                def _mark_pending_payment(self) -> None:
                    {"self._set_status(OrderStatus.PENDING_PAYMENT)" if not public_status else f"{status_writes} = OrderStatus.PENDING_PAYMENT"}

                def confirm(self) -> None:
                    if {status_reads} is not OrderStatus.PENDING_PAYMENT:
                        raise ValueError("only pending payment orders can be confirmed")
                    {"self._set_status(OrderStatus.CONFIRMED)" if not public_status else f"{status_writes} = OrderStatus.CONFIRMED"}
            """,
        )

    def write_order_service(self, *, direct_setattr: bool = False) -> None:
        confirm_body = (
            'setattr(order, "status", OrderStatus.CONFIRMED)\n'
            "                return order"
            if direct_setattr
            else "order.confirm()\n"
            "                return order"
        )
        self.write_file(
            "apps/orders/services.py",
            f"""
            from __future__ import annotations

            from apps.orders.models import Order, OrderStatus

            _ORDERS: dict[str, Order] = {{}}

            def place_order(customer_id: str, items: list[str]) -> Order:
                order = Order.place(customer_id, items)
                _ORDERS[order.id] = order
                return order

            def confirm_order(order_id: str) -> Order:
                order = _ORDERS[order_id]
                {confirm_body}
            """,
        )

    def test_order_public_status_field_fails_boundary_check(self) -> None:
        self.write_order_model(public_status=True)
        self.write_order_service()

        with self.assertRaisesRegex(AssertionError, "externally mutable"):
            self.checker.run_ddd_order_placement(self.workspace)

    def test_order_private_read_only_status_passes_boundary_check(self) -> None:
        self.write_order_model(public_status=False)
        self.write_order_service()

        self.checker.run_ddd_order_placement(self.workspace)

    def test_order_private_lifecycle_state_field_fails_without_guard(self) -> None:
        self.write_order_model(
            public_status=False,
            private_attr="_lifecycle_state",
            guard_private_attr=False,
        )
        self.write_order_service()

        with self.assertRaisesRegex(AssertionError, "externally mutable"):
            self.checker.run_ddd_order_placement(self.workspace)

    def test_order_name_mangled_lifecycle_status_passes_boundary_check(self) -> None:
        self.write_order_model(
            public_status=False,
            private_attr="__lifecycle_status",
            guard_private_attr=False,
        )
        self.write_order_service()

        self.checker.run_ddd_order_placement(self.workspace)

    def test_order_service_setattr_status_mutation_fails_boundary_check(self) -> None:
        self.write_order_model(public_status=False)
        self.write_order_service(direct_setattr=True)

        with self.assertRaisesRegex(AssertionError, "application service"):
            self.checker.run_ddd_order_placement(self.workspace)


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


class CouponTddBehaviorCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.checker = load_checker()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name)
        self.write_package("apps")
        self.write_package("apps/coupons")

    def write_package(self, relative: str) -> None:
        package = self.workspace / relative
        package.mkdir(parents=True, exist_ok=True)
        (package / "__init__.py").write_text("", encoding="utf-8")

    def write_policy(self, *, rejects_used: bool) -> None:
        used_check = self.used_coupon_guard() if rejects_used else ""
        (self.workspace / "apps/coupons/policy.py").write_text(
            "from __future__ import annotations\n\n"
            "from dataclasses import dataclass\n"
            "from datetime import date\n\n\n"
            "@dataclass\n"
            "class Coupon:\n"
            "    code: str\n"
            "    discount_amount: int\n"
            "    minimum_order_amount: int\n"
            "    expires_on: date\n"
            "    used: bool = False\n\n\n"
            "def apply_coupon(coupon: Coupon, order_amount: int, today: date) -> int:\n"
            f"{used_check}"
            "    if today > coupon.expires_on:\n"
            "        raise ValueError(\"coupon expired\")\n"
            "    if order_amount < coupon.minimum_order_amount:\n"
            "        raise ValueError(\"minimum order amount not met\")\n"
            "    return max(order_amount - coupon.discount_amount, 0)\n",
            encoding="utf-8",
        )

    def used_coupon_guard(self) -> str:
        return '    if coupon.used:\n        raise ValueError("coupon already used")\n'

    def test_coupon_policy_boundaries_pass_when_used_coupon_is_rejected(self) -> None:
        self.write_policy(rejects_used=True)

        self.checker.run_coupon_tdd_policy_boundaries(self.workspace)

    def test_coupon_policy_boundaries_fail_when_used_coupon_is_accepted(self) -> None:
        self.write_policy(rejects_used=False)

        with self.assertRaisesRegex(AssertionError, "used coupon"):
            self.checker.run_coupon_tdd_policy_boundaries(self.workspace)

    def test_coupon_red_proof_fails_after_removing_used_coupon_guard(self) -> None:
        self.write_policy(rejects_used=True)
        (self.workspace / "tests").mkdir(parents=True, exist_ok=True)
        (self.workspace / "tests/__init__.py").write_text("", encoding="utf-8")
        (self.workspace / "tests/test_coupons.py").write_text(
            "from __future__ import annotations\n\n"
            "import unittest\n"
            "from datetime import date\n\n"
            "from apps.coupons.policy import Coupon, apply_coupon\n\n\n"
            "class CouponPolicyTests(unittest.TestCase):\n"
            "    def test_used_coupon_is_rejected(self) -> None:\n"
            "        coupon = Coupon('USED', 1000, 5000, date(2026, 1, 31), used=True)\n"
            "        with self.assertRaises(ValueError):\n"
            "            apply_coupon(coupon, 5000, date(2026, 1, 31))\n",
            encoding="utf-8",
        )

        exit_code = self.checker.run_coupon_tdd_red_proof(self.workspace)

        self.assertNotEqual(0, exit_code)

    def test_coupon_red_proof_mutates_alternate_used_coupon_guard(self) -> None:
        self.write_policy(rejects_used=True)
        policy_path = self.workspace / "apps/coupons/policy.py"
        policy_path.write_text(
            policy_path.read_text(encoding="utf-8").replace(
                '    if coupon.used:\n        raise ValueError("coupon already used")\n',
                '    if coupon.used is True:\n        raise ValueError("already used")\n',
            ),
            encoding="utf-8",
        )
        (self.workspace / "tests").mkdir(parents=True, exist_ok=True)
        (self.workspace / "tests/__init__.py").write_text("", encoding="utf-8")
        (self.workspace / "tests/test_coupons.py").write_text(
            "from __future__ import annotations\n\n"
            "import unittest\n"
            "from datetime import date\n\n"
            "from apps.coupons.policy import Coupon, apply_coupon\n\n\n"
            "class CouponPolicyTests(unittest.TestCase):\n"
            "    def test_used_coupon_is_rejected(self) -> None:\n"
            "        coupon = Coupon('USED', 1000, 5000, date(2026, 1, 31), used=True)\n"
            "        with self.assertRaises(ValueError):\n"
            "            apply_coupon(coupon, 5000, date(2026, 1, 31))\n",
            encoding="utf-8",
        )

        exit_code = self.checker.run_coupon_tdd_red_proof(self.workspace)

        self.assertEqual(1, exit_code)

    def test_coupon_red_proof_returns_two_when_guard_is_missing(self) -> None:
        self.write_policy(rejects_used=False)
        (self.workspace / "tests").mkdir(parents=True, exist_ok=True)
        (self.workspace / "tests/__init__.py").write_text("", encoding="utf-8")
        (self.workspace / "tests/test_coupons.py").write_text(
            "from __future__ import annotations\n\n"
            "import unittest\n\n\n"
            "class CouponPolicyTests(unittest.TestCase):\n"
            "    def test_placeholder(self) -> None:\n"
            "        self.assertTrue(True)\n",
            encoding="utf-8",
        )

        exit_code = self.checker.run_coupon_tdd_red_proof(self.workspace)

        self.assertEqual(2, exit_code)


if __name__ == "__main__":
    unittest.main()
