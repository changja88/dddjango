"""bad_frame_two_aggregate_types — 틀의 쓰기 도구가 한 작업 단위 구간에서 두 애그리거트 리포지토리에 쓴다(#546 · 틀 넓힘)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class CheckoutOrderFrame:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def find_order(self, order_id: str) -> Order:
        return self._order_repository.get(order_id)

    def find_stock(self, sku: str) -> Stock:
        return self._stock_repository.get(sku)

    def save_order_and_stock(self, order: Order, stock: Stock) -> None:
        with self._unit_of_work:
            self._order_repository.save(order)
            self._stock_repository.save(stock)
