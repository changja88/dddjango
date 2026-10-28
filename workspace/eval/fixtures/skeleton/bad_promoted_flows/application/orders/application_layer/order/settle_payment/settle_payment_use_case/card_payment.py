from __future__ import annotations

from .settle_payment_frame import SettlePaymentFrame


class CardPaymentUseCase:
    def __init__(self, frame: SettlePaymentFrame) -> None:
        self._frame: SettlePaymentFrame = frame

    def run(self, payment_id: int) -> None:
        self._frame.record_done(payment_id)
