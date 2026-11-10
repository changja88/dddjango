"""bad 행 2 — 쓰기와 `break` 사이에 다른 이름의 쓰기가 있다(애그리거트 둘을 바꾼다)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class CancelFirstAndRenameTargetUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            target: Order = self._order_repository.get(other_id)
            found: list[Order] = self._order_repository.find_by_customer(customer_id)
            for order in found:
                order.cancel()
                self._order_repository.save(order)
                target.rename(order.order_id)
                self._order_repository.save_label(target)
                break
