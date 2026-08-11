from __future__ import annotations

from enum import Enum


class OrderStage(Enum):
    PLACING = "place_order"
    DONE = "done"
