from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository

from .order_payment_failure import OrderPaymentFailure
from .payment_channel import _PaymentChannel


class PlaceOrderUseCase:
    def __init__(self, repository: OrderRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: OrderRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, order_id: str, amount: int) -> None:
        channel: _PaymentChannel = _PaymentChannel(order_id)
        with self._unit_of_work:
            order: Order = self._repository.get(order_id)
            if not order.pay(amount):
                raise OrderPaymentFailure(order_id)
            self._repository.save(order)
        channel.close()
