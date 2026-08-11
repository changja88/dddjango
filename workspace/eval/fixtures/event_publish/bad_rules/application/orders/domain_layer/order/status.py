from __future__ import annotations

from enum import Enum


class OrderStatus(Enum):
    RECORDING = "record_settlement"
    DONE = "done"
