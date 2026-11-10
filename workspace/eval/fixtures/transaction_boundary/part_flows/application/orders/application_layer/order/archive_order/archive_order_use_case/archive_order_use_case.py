from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .archive_order_frame import ArchiveOrderFrame
from .order_archive import OrderArchive


class ArchiveOrderUseCase:
    def __init__(self, order_repository: OrderRepository, new_unit_of_work: Callable[[], OrdersUnitOfWork]) -> None:
        self._frame: ArchiveOrderFrame = ArchiveOrderFrame(order_repository, new_unit_of_work)
        self._order_archive: OrderArchive = OrderArchive(self._frame)

    def execute(self, order_id: str) -> bool:
        return self._order_archive.run(order_id)
