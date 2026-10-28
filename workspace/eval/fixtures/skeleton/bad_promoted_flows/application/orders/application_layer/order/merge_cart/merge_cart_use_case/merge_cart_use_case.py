from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.merge_cart.merge_cart_command import MergeCartCommand
from application.orders.application_layer.order.merge_cart.merge_cart_result import MergeCartResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .cart_price import CartPrice
from .cart_tax import CartTax
from .merge_cart_frame import MergeCartFrame


class MergeCartUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: MergeCartFrame = MergeCartFrame(new_unit_of_work)
        self._cart_tax: CartTax = CartTax(frame=self._frame)
        self._cart_price: CartPrice = CartPrice(frame=self._frame, cart_tax=self._cart_tax)

    def execute(self, command: MergeCartCommand) -> MergeCartResult:
        self._cart_price.total(command.target_id)
        return MergeCartResult(target_id=command.target_id, done=True)
