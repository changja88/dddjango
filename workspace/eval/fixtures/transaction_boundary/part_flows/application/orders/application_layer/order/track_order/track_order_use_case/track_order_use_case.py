from __future__ import annotations

from collections.abc import Callable

from application.orders.application_layer.port.order_stream.order_stream_port import OrderStreamPort
from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository

from .track_feed import TrackFeed
from .track_order_frame import TrackOrderFrame


class TrackOrderUseCase:
    def __init__(
        self,
        order_repository: OrderRepository,
        new_unit_of_work: Callable[[], OrdersUnitOfWork],
        order_stream: OrderStreamPort,
    ) -> None:
        self._frame: TrackOrderFrame = TrackOrderFrame(order_repository, new_unit_of_work)
        self._track_feed: TrackFeed = TrackFeed(self._frame, order_stream)

    def execute(self, order_id: str) -> bool:
        return self._track_feed.run(order_id)
