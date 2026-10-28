from __future__ import annotations

from .renew_plan_frame import RenewPlanFrame


class CardRenewal:
    def __init__(self, frame: RenewPlanFrame) -> None:
        self._frame: RenewPlanFrame = frame

    def renew(self, plan_id: int) -> None:
        self._frame.record_done(plan_id)
