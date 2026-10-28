from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.grant_badge.grant_badge_command import GrantBadgeCommand
from application.orders.application_layer.order.grant_badge.grant_badge_result import GrantBadgeResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .badge_grant import BadgeGrant
from .grant_badge_frame import GrantBadgeFrame


class GrantBadgeUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: GrantBadgeFrame = GrantBadgeFrame(new_unit_of_work)
        self._badge_grant: BadgeGrant = BadgeGrant(frame=self._frame)

    def execute(self, command: GrantBadgeCommand) -> GrantBadgeResult:
        self._badge_grant._run(command.target_id)
        self._frame._commit_badge(command.target_id)
        return GrantBadgeResult(target_id=command.target_id, done=True)
