"""bad 행 3 — 따로 조회한 주문 둘을 한 트랜잭션에서 차례로 저장한다(이체 꼴 · 함께 커밋 표지 없음)."""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class TransferBetweenOrdersUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str) -> None:
        with self._unit_of_work:
            source: Order = self._order_repository.get(order_id)
            target: Order = self._order_repository.get_for_update(other_id)
            source.cancel()
            target.rename(order_id)
            self._order_repository.save(source)
            self._order_repository.save(target)
