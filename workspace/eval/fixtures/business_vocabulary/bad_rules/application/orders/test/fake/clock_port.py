from __future__ import annotations

from framework.clock.clock_port import ClockPort


class FakeClock(ClockPort):
    def now(self) -> int:
        return 0
