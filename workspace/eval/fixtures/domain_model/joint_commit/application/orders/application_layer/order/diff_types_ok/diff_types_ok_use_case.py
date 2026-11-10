"""0 줄 — 다른 타입: `잠금` 칸 차례(order → stock)대로 처음 잠근다"""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class Conflict(Exception):
    pass


class DiffTypesOkUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str, sku: str) -> None:
        # joint-commit: 함께 order, stock  잠금 order(order_id) → stock(sku)  불변식 옮긴 요청은 정확히 한 주문에만 있다
        with self._unit_of_work:
            order: Order = self._order_repository.get(order_id)
            stock: Stock = self._stock_repository.get(sku)
            order.cancel()
            stock.reserve(1)
            self._order_repository.save(order)
            self._stock_repository.save(stock)
