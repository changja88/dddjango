"""bad 행 3 — `if <그냥 save a>: return`(save 는 -> None) 뒤 b 쓰기 — CAS 가 아니면 배타가 아니다."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class SavePlainThenReturnUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            first: Order = self._order_repository.get(order_id)
            second: Order = self._order_repository.get(other_id)
            first.cancel()
            second.rename(first.order_id)
            if self._order_repository.save(first):
                return
            self._order_repository.save(second)
