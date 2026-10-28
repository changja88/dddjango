from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.pay_invoice.pay_invoice_command import PayInvoiceCommand
from application.orders.application_layer.order.pay_invoice.pay_invoice_result import PayInvoiceResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .invoice_payment import InvoicePayment
from .pay_invoice_frame import PayInvoiceFrame


class PayInvoiceUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: PayInvoiceFrame = PayInvoiceFrame(new_unit_of_work)
        self._invoice_payment: InvoicePayment = InvoicePayment(frame=self._frame)

    def _retry_payment(self, target_id: int) -> None:
        self._frame.record_done(target_id)

    def execute(self, command: PayInvoiceCommand) -> PayInvoiceResult:
        invoice_id: int = command.target_id
        self._invoice_payment.run(invoice_id, on_retry=lambda: self._retry_payment(invoice_id))
        return PayInvoiceResult(target_id=command.target_id, done=True)
