from __future__ import annotations

from typing import TYPE_CHECKING

from application.orders.application_layer.order.pack_box.pack_box_use_case.pack_box_use_case import PACK_LIMIT

from .pack_box_frame import PackBoxFrame

if TYPE_CHECKING:
    from .pack_box_use_case import PackBoxUseCase


class BoxFill:
    def __init__(self, frame: PackBoxFrame) -> None:
        self._frame: PackBoxFrame = frame

    def fill(self, box_id: int, count: int) -> None:
        if count <= PACK_LIMIT:
            self._frame.record_done(box_id)
