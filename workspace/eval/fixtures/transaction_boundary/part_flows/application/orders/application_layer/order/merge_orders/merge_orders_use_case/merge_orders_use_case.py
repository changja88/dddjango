from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .merge_orders_frame import MergeOrdersFrame
from .order_merge import OrderMerge


class MergeOrdersUseCase:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._frame: MergeOrdersFrame = MergeOrdersFrame(order_repository, new_unit_of_work)
        self._order_merge: OrderMerge = OrderMerge(self._frame)

    def execute(self, source_id: str, target_id: str) -> bool:
        return self._order_merge.run(source_id, target_id)
