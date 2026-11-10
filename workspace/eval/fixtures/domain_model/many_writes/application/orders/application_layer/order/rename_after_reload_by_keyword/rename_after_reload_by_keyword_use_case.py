"""ok 같은 인자 값을 키워드로 다시 읽은 이름도 같은 애그리거트다(키워드 이름은 보지 않는다 · 구현 검토 C 중요 1)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class RenameAfterReloadByKeywordUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            order: Order = self._order_repository.get(order_id)
            order.cancel()
            self._order_repository.save(order)
            again: Order = self._order_repository.get_for_update(order_id=order_id)
            again.rename(customer_id)
            self._order_repository.save(again)
