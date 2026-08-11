from __future__ import annotations


class Order:
    def settle(self) -> None:
        self._settled: bool = True
