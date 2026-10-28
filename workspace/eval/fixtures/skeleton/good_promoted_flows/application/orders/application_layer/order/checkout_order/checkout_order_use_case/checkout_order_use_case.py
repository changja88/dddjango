from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.checkout_order.checkout_order_command import CheckoutOrderCommand
from application.orders.application_layer.order.checkout_order.checkout_order_result import CheckoutOrderResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.order.value_object.payment_route import PaymentRoute

from .bank_transfer import BankTransfer
from .card_payment import CardPayment
from .checkout_memory import _CheckoutMemory
from .checkout_order_frame import CheckoutOrderFrame
from .stock_hold import StockHold


class CheckoutOrderUseCase:
    def __init__(self, order_repository: OrderRepository,
                 new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: CheckoutOrderFrame = CheckoutOrderFrame(order_repository, new_unit_of_work)
        self._stock_hold: StockHold = StockHold(frame=self._frame)
        self._card_payment: CardPayment = CardPayment(frame=self._frame, stock_hold=self._stock_hold)
        self._bank_transfer: BankTransfer = BankTransfer(frame=self._frame, stock_hold=self._stock_hold)

    def execute(self, command: CheckoutOrderCommand) -> CheckoutOrderResult:
        order: Order = self._frame.find_order(command.target_id)
        memory: _CheckoutMemory = _CheckoutMemory(order_id=command.target_id)
        match order.payment_route(command.requested_route):
            case PaymentRoute.CARD:
                self._card_payment.run(memory)
            case PaymentRoute.BANK:
                self._bank_transfer.run(memory)
        return CheckoutOrderResult(target_id=command.target_id, done=memory.paid)
