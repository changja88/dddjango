from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .card_payment import CardPayment
from .checkout_order_frame import CheckoutOrderFrame


class CheckoutOrderUseCase:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._frame: CheckoutOrderFrame = CheckoutOrderFrame(order_repository, new_unit_of_work)
        self._card_payment: CardPayment = CardPayment(self._frame)

    def execute(self, order_id: str, amount: int) -> bool:
        return self._card_payment.run(order_id, amount)
