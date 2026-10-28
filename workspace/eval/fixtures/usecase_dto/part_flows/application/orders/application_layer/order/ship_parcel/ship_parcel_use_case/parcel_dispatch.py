"""cand_part_rule — 흐름 부품의 공개 메서드가 도메인 속성 깊이를 들여다보는 조건을 둔다(ⓓ#194 후보 · 부품 넓힘)."""
from __future__ import annotations

from application.orders.domain_layer.order.order import Order

from .ship_parcel_frame import ShipParcelFrame


class ParcelDispatch:
    def __init__(self, frame: ShipParcelFrame) -> None:
        self._frame: ShipParcelFrame = frame

    def dispatch(self, order_id: str) -> None:
        order: Order = self._frame.load_order(order_id)
        if order.shipping.country == "KR":
            order.ship_domestic()
        else:
            order.ship_abroad()
        self._frame.save_shipped(order)
