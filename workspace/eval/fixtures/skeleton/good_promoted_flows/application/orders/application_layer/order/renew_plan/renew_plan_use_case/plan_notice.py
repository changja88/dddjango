from __future__ import annotations

from .renew_plan_frame import RenewPlanFrame


class PlanNotice:
    def __init__(self, frame: RenewPlanFrame) -> None:
        self._frame: RenewPlanFrame = frame

    def send(self, order_id: int) -> None:
        self._frame.record_notice(order_id)
