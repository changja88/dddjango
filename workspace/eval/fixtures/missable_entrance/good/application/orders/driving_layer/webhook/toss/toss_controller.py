from __future__ import annotations

from application.orders.composition_root.dependency_wiring import build_record_payment
from framework.web.signature import verified


class TossController:
    @verified
    def on_payment(self, payload: str) -> str:
        use_case = build_record_payment()
        return use_case.execute(payload)
