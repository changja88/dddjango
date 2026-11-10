"""#546 무변 — 서로 다른 저장소 타입 둘은 #546 몫이라 #550 은 다시 내지 않는다."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class MoveOrderAndStockUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            order: Order = self._order_repository.get(order_id)
            stock: Stock = self._stock_repository.get(other_id)
            order.cancel()
            stock.reserve(1)
            self._order_repository.save(order)
            self._stock_repository.save(stock)
