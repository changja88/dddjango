from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.settle_payment.settle_payment_command import SettlePaymentCommand
from application.orders.application_layer.order.settle_payment.settle_payment_result import SettlePaymentResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .card_payment import CardPaymentUseCase
from .settle_payment_frame import SettlePaymentFrame


class SettlePaymentUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: SettlePaymentFrame = SettlePaymentFrame(new_unit_of_work)
        self._card_payment: CardPaymentUseCase = CardPaymentUseCase(frame=self._frame)

    def execute(self, command: SettlePaymentCommand) -> SettlePaymentResult:
        self._card_payment.run(command.target_id)
        return SettlePaymentResult(target_id=command.target_id, done=True)
