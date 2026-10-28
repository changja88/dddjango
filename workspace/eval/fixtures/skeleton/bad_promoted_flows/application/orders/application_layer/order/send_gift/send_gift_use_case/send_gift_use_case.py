from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.send_gift.send_gift_command import SendGiftCommand
from application.orders.application_layer.order.send_gift.send_gift_result import SendGiftResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .gift_card_payment import GiftCardPayment
from .gift_memory import GiftMemory
from .send_gift_frame import SendGiftFrame


class SendGiftUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: SendGiftFrame = SendGiftFrame(new_unit_of_work)
        self._gift_card_payment: GiftCardPayment = GiftCardPayment()

    def execute(self, command: SendGiftCommand) -> SendGiftResult:
        memory: GiftMemory = GiftMemory(gift_id=command.target_id)
        self._gift_card_payment.pay(memory)
        self._frame.record_gift(memory)
        return SendGiftResult(target_id=command.target_id, done=memory.paid)
