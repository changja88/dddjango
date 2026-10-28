from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.pack_box.pack_box_command import PackBoxCommand
from application.orders.application_layer.order.pack_box.pack_box_result import PackBoxResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .box_fill import BoxFill
from .pack_box_frame import PackBoxFrame

PACK_LIMIT: int = 20


class PackBoxUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: PackBoxFrame = PackBoxFrame(new_unit_of_work)
        self._box_fill: BoxFill = BoxFill(frame=self._frame)

    def execute(self, command: PackBoxCommand) -> PackBoxResult:
        self._box_fill.fill(command.target_id, count=3)
        return PackBoxResult(target_id=command.target_id, done=True)
