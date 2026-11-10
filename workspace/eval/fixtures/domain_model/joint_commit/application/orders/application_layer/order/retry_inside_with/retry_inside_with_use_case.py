"""#546 + #550 — 승인 구간 안 다시 하는 고리(첫째에 두 번 적용)"""
from __future__ import annotations

from django.db import transaction

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class Conflict(Exception):
    pass


class RetryInsideWithUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str, sku: str) -> None:
        # joint-commit: 함께 order×2  잠금 order(order_id)  불변식 옮긴 요청은 정확히 한 주문에만 있다
        with self._unit_of_work:
            for attempt in range(3):
                source: Order = self._order_repository.get(order_id)
                target: Order = self._order_repository.get(other_id)
                source.cancel()
                target.move_to(source.order_id)
                saved: list[bool] = [self._order_repository.save_with_version_guard(o) for o in sorted((source, target), key=lambda item: item.order_id)]
                if all(saved):
                    break
