from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.renew_plan.renew_plan_command import RenewPlanCommand
from application.orders.application_layer.order.renew_plan.renew_plan_result import RenewPlanResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from application.orders.domain_layer.order.order_repository import OrderRepository

from .plan_notice import PlanNotice
from .renew_plan_frame import RenewPlanFrame


class RenewPlanUseCase:
    def __init__(self, order_repository: OrderRepository,
                 new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: RenewPlanFrame = RenewPlanFrame(order_repository, new_unit_of_work)
        self._plan_notice: PlanNotice = PlanNotice(frame=self._frame)

    def execute(self, command: RenewPlanCommand) -> RenewPlanResult:
        months: int = command.months
        self._frame.commit_plan_change(command.target_id, change=lambda order: order.pay(months))
        self._plan_notice.send(command.target_id)
        return RenewPlanResult(target_id=command.target_id, done=True)
