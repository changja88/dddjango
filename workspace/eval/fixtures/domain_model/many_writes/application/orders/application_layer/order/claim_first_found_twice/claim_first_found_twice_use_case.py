"""ok 첫 것을 잡아 같은 애그리거트를 두 번 쓰고 `break`(`save` → `save_label` — 한 건만 바꾼다)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class ClaimFirstFoundTwiceUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            found: list[Order] = self._order_repository.find_by_customer(customer_id)
            for order in found:
                if not order.is_open():
                    continue
                order.cancel()
                self._order_repository.save(order)
                order.rename(other_id)
                self._order_repository.save_label(order)
                break
