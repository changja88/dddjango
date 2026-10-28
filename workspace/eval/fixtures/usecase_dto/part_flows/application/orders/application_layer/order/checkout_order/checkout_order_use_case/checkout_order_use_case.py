"""②′ 폴더 본체 — `__init__` 이 틀 → 갈래 차례로 부품을 만든다."""
from __future__ import annotations

from application.orders.application_layer.order.checkout_order.checkout_order_command import CheckoutOrderCommand
from application.orders.application_layer.order.checkout_order.checkout_order_result import CheckoutOrderResult
from application.orders.domain_layer.order.order_repository import OrderRepository

from .card_payment import CardPayment
from .checkout_order_frame import CheckoutOrderFrame


class CheckoutOrderUseCase:
    def __init__(self, order_repository: OrderRepository) -> None:
        self._frame: CheckoutOrderFrame = CheckoutOrderFrame(order_repository)
        self._card_payment: CardPayment = CardPayment(frame=self._frame)

    def execute(self, command: CheckoutOrderCommand) -> CheckoutOrderResult:
        self._card_payment.pay(command.order_id)
        return CheckoutOrderResult(order_id=command.order_id)
