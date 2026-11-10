"""#546 + #550 — 새 주문 이름 `order` 를 고정 차례 고리 변수로 다시 씀(반복 변수는 고리의 글자 원소로만 가린다)"""
from __future__ import annotations

from django.db import transaction

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class Conflict(Exception):
    pass


class MergeReusedNameFixedOrderUseCase:
    def __init__(self, order_repository: OrderRepository,
                 stock_repository: StockRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, first_id: str, second_id: str) -> None:
        # joint-commit: 함께 order×3  잠금 order(order_id)  불변식 옮긴 요청은 정확히 한 주문에만 있다
        with self._unit_of_work:
            first: Order = self._order_repository.get(first_id)
            second: Order = self._order_repository.get(second_id)
            order = Order(first_id + "+" + second_id)
            self._order_repository.save(order)
            for order in (first, second):
                order.cancel()
                if not self._order_repository.save_with_version_guard(order):
                    raise Conflict()
