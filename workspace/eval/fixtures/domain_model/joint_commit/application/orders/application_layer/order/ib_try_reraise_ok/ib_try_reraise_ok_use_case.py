"""0 줄 — 구간 안 try 의 except 가 다른 예외로 다시 올린다(삼키지 않음)"""
from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class Conflict(Exception):
    pass


class IbTryReraiseOkUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str, sku: str) -> None:
        # joint-commit: 함께 order×2  잠금 order(order_id)  불변식 옮긴 요청은 정확히 한 주문에만 있다
        with self._unit_of_work:
            source: Order = self._order_repository.get(order_id)
            target: Order = self._order_repository.get(other_id)
            source.cancel()
            target.move_to(source.order_id)
            try:
                for order in sorted((source, target), key=lambda item: item.order_id):
                    if not self._order_repository.save_with_version_guard(order):
                        raise Conflict()
            except Conflict as exc:
                raise ValueError("충돌") from exc
