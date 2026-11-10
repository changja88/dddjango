"""ok CAS 결과 이름의 `if <이름>: return` 뒤 쓰기는 첫 쓰기가 미스였던 길이다(둘 가운데 하나만 바꾼다)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class ClaimPrimaryOrFallbackUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            primary: Order = self._order_repository.get(order_id)
            fallback: Order = self._order_repository.get(other_id)
            primary.cancel()
            fallback.cancel()
            claimed: bool = self._order_repository.save_with_version_guard(primary)
            if claimed:
                return
            if not self._order_repository.save_with_version_guard(fallback):
                raise RuntimeError(other_id)
