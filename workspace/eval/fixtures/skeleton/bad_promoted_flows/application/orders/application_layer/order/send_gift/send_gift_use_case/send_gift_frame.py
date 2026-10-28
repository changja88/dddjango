from __future__ import annotations

from typing import Callable

from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .gift_card_payment import GiftCardPayment
from .gift_memory import GiftMemory


class SendGiftFrame:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._new_unit_of_work: Callable[[], OrderUnitOfWork] = new_unit_of_work

    def record_gift(self, memory: GiftMemory) -> None:
        if isinstance(memory, GiftCardPayment):
            return
        with self._new_unit_of_work() as unit_of_work:
            unit_of_work.mark_done(memory.gift_id)
