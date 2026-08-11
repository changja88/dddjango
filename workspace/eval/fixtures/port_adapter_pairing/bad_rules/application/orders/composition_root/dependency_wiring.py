from __future__ import annotations

from application.orders.test.fake.clock_port import FakeClock


def build_notify() -> object:
    return FakeClock()
