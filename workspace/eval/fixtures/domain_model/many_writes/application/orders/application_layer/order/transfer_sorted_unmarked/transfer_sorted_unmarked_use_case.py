"""bad 행 3 — 키 정렬 글자 고리로 CAS 저장해도 표지가 없으면 이체 꼴이다(글자 고리 원소마다 쓴 것)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class TransferSortedUnmarkedUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            source: Order = self._order_repository.get(order_id)
            target: Order = self._order_repository.get(other_id)
            source.cancel()
            target.rename(source.order_id)
            for order in sorted((source, target), key=lambda item: item.order_id):
                if not self._order_repository.save_with_version_guard(order):
                    raise RuntimeError(order.order_id)
