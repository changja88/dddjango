from __future__ import annotations

from functools import partial
from typing import Callable

from application.orders.application_layer.order.print_label.print_label_command import PrintLabelCommand
from application.orders.application_layer.order.print_label.print_label_result import PrintLabelResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .label_print import LabelPrint
from .print_label_frame import PrintLabelFrame


class PrintLabelUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: PrintLabelFrame = PrintLabelFrame(new_unit_of_work)
        self._label_print: LabelPrint = LabelPrint(frame=self._frame)

    def _retry_print(self, target_id: int) -> None:
        self._frame.record_done(target_id)

    def execute(self, command: PrintLabelCommand) -> PrintLabelResult:
        label_id: int = command.target_id
        self._label_print.run(label_id, on_retry=partial(self._retry_print, label_id))
        return PrintLabelResult(target_id=command.target_id, done=True)
