from __future__ import annotations

import redis


class FakeClock:
    def now(self) -> int:
        return 0
