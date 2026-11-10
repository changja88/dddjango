"""ok 글자 고리에서 CAS 가 처음 맞은 하나만 쓰고 나간다(참 갈래가 고리를 나감)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class ClaimFirstOfPairUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            primary: Order = self._order_repository.get(order_id)
            fallback: Order = self._order_repository.get(other_id)
            for candidate in (primary, fallback):
                candidate.cancel()
                if self._order_repository.save_with_version_guard(candidate):
                    break
