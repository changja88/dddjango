"""bad 행 3 — 고리 안 `if <CAS a>: return` — 미스 회차에 b 를 쓰고 다음 회차에 a 가 맞을 수 있다."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class ClaimInRetryLoopUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            primary: Order = self._order_repository.get(order_id)
            backup: Order = self._order_repository.get(other_id)
            for _attempt in range(3):
                primary.cancel()
                if self._order_repository.save_with_version_guard(primary):
                    return
                backup.rename(customer_id)
                self._order_repository.save(backup)
