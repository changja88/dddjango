"""ok CAS 결과를 이름에 담고 바로 다음 문장 `if not <이름>:` — 미스 몸의 쓰기는 첫 쓰기와 배타다(구현 검토 C 중요 1)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class CancelReloadByResultNameUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            order: Order = self._order_repository.get(order_id)
            order.cancel()
            saved: bool = self._order_repository.save_with_version_guard(order)
            if not saved:
                fresh: Order = self._order_repository.get_for_update(order.order_id)
                fresh.cancel()
                self._order_repository.save(fresh)
