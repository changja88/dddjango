from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.payment_gateway.payment_gateway_port import PaymentGatewayPort
from application.orders.application_layer.port.receipt_archive.receipt_archive_port import ReceiptArchivePort
from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .card_charge import CardCharge
from .charge_order_frame import ChargeOrderFrame


class ChargeOrderUseCase:
    def __init__(
        self,
        order_repository: OrderRepository,
        new_unit_of_work: Callable[[], OrdersUnitOfWork],
        payment_gateway: PaymentGatewayPort,
        receipt_archive: ReceiptArchivePort,
    ) -> None:
        self._frame: ChargeOrderFrame = ChargeOrderFrame(order_repository, new_unit_of_work)
        self._card_charge: CardCharge = CardCharge(self._frame, payment_gateway, receipt_archive)

    def execute(self, order_id: str, amount: int) -> bool:
        return self._card_charge.run(order_id, amount)
