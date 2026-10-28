"""②′ 폴더 본체 — `__init__` 이 틀 → 갈래 차례로 부품을 만든다(본체 몸에는 읽기 · 쓰기가 없다)."""
from __future__ import annotations

from application.orders.application_layer.order.checkout_order.checkout_order_command import CheckoutOrderCommand
from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock_repository import StockRepository

from .card_payment import CardPayment
from .checkout_order_frame import CheckoutOrderFrame


class CheckoutOrderUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._frame: CheckoutOrderFrame = CheckoutOrderFrame(order_repository, stock_repository, unit_of_work)
        self._card_payment: CardPayment = CardPayment(frame=self._frame)

    def execute(self, command: CheckoutOrderCommand) -> None:
        self._card_payment.pay(command.order_id, command.sku, command.line)
