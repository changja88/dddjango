"""bad_flows_sibling_function — 본체가 형제 모듈의 맨 위 함수(`from` import 한 이름 · 모듈 별칭 `m.<함수>`)와
모듈 별칭의 클래스 생성(`m.<클래스>(…)`)에 본체 객체를 넘긴다(#660 — 클래스 대신 함수로 비켜 가는 꼴)."""
from __future__ import annotations

from typing import Callable

import application.orders.application_layer.order.renew_plan.renew_plan_use_case.plan_receipt as receipt
from application.orders.application_layer.order.renew_plan.renew_plan_command import RenewPlanCommand
from application.orders.application_layer.order.renew_plan.renew_plan_result import RenewPlanResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from . import plan_notice
from .bank_renewal import renew_by_bank
from .card_renewal import CardRenewal
from .renew_plan_frame import RenewPlanFrame


class RenewPlanUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: RenewPlanFrame = RenewPlanFrame(new_unit_of_work)
        self._card_renewal: CardRenewal = CardRenewal(frame=self._frame)

    def charge_again(self, plan_id: int) -> None:
        self._card_renewal.renew(plan_id)

    def execute(self, command: RenewPlanCommand) -> RenewPlanResult:
        renew_by_bank(self, command.target_id)
        plan_notice.send_notice(command.target_id, owner=self)
        receipt.PlanReceipt(self.charge_again).issue(command.target_id)
        return RenewPlanResult(target_id=command.target_id, done=True)
