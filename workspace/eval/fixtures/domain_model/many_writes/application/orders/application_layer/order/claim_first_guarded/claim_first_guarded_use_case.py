"""ok 첫 것을 CAS 로 잡고 나간다 — 쓰기가 `if` 검사식이고 참 갈래가 `return`(거짓이면 쓰지 않았다)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class ClaimFirstGuardedUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            found: list[Order] = self._order_repository.find_by_customer(customer_id)
            for order in found:
                order.cancel()
                if self._order_repository.save_with_version_guard(order):
                    return
