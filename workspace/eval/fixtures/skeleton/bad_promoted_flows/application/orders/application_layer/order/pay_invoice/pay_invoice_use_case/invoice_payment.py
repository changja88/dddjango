from __future__ import annotations

from typing import Callable

from .pay_invoice_frame import PayInvoiceFrame


class InvoicePayment:
    def __init__(self, frame: PayInvoiceFrame) -> None:
        self._frame: PayInvoiceFrame = frame

    def run(self, target_id: int, on_retry: Callable[[], None]) -> None:
        self._frame.record_done(target_id)
        on_retry()
