from __future__ import annotations


class DjangoOrderRepository:
    def save_all(self, orders: object) -> None:
        for order in orders:
            row = self._locked_row(order)
            row.apply(order)

    def _locked_row(self, order: object) -> object:
        return order
