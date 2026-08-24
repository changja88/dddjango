from __future__ import annotations

from application.orders.domain_layer.bin.event.bin_moved import BinMoved


class Bin:
    def __init__(self, bin_id: str) -> None:
        self.bin_id: str = bin_id
        self._events: list = []

    def move(self) -> None:
        self._events.append(BinMoved())

    def pull_events(self) -> list:
        drained: list = list(self._events)
        self._events.clear()
        return drained
