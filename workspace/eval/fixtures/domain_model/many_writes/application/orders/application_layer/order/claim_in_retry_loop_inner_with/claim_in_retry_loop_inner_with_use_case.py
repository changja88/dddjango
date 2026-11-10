"""bad 행 3 — 구간 안 고리 · 참 갈래 return 이 안쪽 `with`(트랜잭션 아님) 안 — 미스 회차에 b 를 쓴다."""
from __future__ import annotations

import contextlib

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class ClaimInRetryLoopInnerWithUseCase:
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
                with contextlib.suppress(KeyError):
                    if self._order_repository.save_with_version_guard(primary):
                        return
                backup.rename(customer_id)
                self._order_repository.save(backup)
