from __future__ import annotations

import tenacity


class PaymentAdapter:
    def charge(self, amount: int) -> None:
        return None


class PaymentBreaker:
    pass
