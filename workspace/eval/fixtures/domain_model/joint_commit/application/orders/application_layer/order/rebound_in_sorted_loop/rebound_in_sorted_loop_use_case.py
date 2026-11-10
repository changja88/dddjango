"""0 줄 — 키 정렬 고리 안 `order = order.renamed()` 는 새 것이 아니다(칸 `order×2`)"""
from __future__ import annotations

from django.db import transaction

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class Conflict(Exception):
    pass


class ReboundInSortedLoopUseCase:
    def __init__(self, order_repository: OrderRepository,
                 stock_repository: StockRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, a_id: str, b_id: str) -> None:
        # joint-commit: 함께 order×2  잠금 order(order_id)  불변식 옮긴 요청은 정확히 한 주문에만 있다
        with self._unit_of_work:
            a: Order = self._order_repository.get(a_id)
            b: Order = self._order_repository.get(b_id)
            for order in sorted((a, b), key=lambda item: item.order_id):
                order = order.renamed()
                if not self._order_repository.save_with_version_guard(order):
                    raise Conflict()
