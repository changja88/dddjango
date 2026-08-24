from __future__ import annotations

from application.orders.domain_layer.stock.stock_repository import StockRepository


class DjangoStockRepository(StockRepository):
    def get(self, stock_id: str) -> object:
        return None

    def save(self, stock: object) -> None:
        if stock._events:
            raise PendingEventsGuard()  # noqa: F821
        StockModel.objects.filter(pk=stock.stock_id).update()  # noqa: F821

