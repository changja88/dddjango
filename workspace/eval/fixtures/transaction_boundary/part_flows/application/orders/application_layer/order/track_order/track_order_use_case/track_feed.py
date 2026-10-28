from __future__ import annotations

from application.orders.application_layer.port.order_stream.order_stream_port import OrderStreamPort

from .track_order_frame import TrackOrderFrame


class TrackFeed:
    def __init__(self, frame: TrackOrderFrame, order_stream: OrderStreamPort) -> None:
        self._frame: TrackOrderFrame = frame
        self._order_stream: OrderStreamPort = order_stream

    def run(self, order_id: str) -> bool:
        if not self._frame.commit_order_change(order_id, lambda current: current.ship()):
            return False
        self._order_stream.publish_item(order_id)
        return True
