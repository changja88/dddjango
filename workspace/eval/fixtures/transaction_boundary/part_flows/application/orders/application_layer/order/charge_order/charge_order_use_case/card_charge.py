from __future__ import annotations

from application.orders.application_layer.port.payment_gateway.payment_gateway_port import PaymentGatewayPort
from application.orders.application_layer.port.receipt_archive.receipt_archive_port import ReceiptArchivePort

from .charge_order_frame import ChargeOrderFrame


class CardCharge:
    def __init__(
        self, frame: ChargeOrderFrame, payment_gateway: PaymentGatewayPort, receipt_archive: ReceiptArchivePort
    ) -> None:
        self._frame: ChargeOrderFrame = frame
        self._payment_gateway: PaymentGatewayPort = payment_gateway
        self._receipt_archive: ReceiptArchivePort = receipt_archive

    def run(self, order_id: str, amount: int) -> bool:
        self._payment_gateway.reserve(order_id, amount)
        if not self._frame.commit_order_change(order_id, lambda current: current.pay(amount)):
            return False
        self._receipt_archive.save_record(order_id)
        return True
