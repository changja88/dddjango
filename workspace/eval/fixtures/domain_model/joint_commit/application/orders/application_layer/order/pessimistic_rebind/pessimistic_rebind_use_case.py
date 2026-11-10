"""0 줄 — 꼴 P: 잠근 뒤 원래 이름으로 다시 묶어 저장"""
from __future__ import annotations

from django.db import transaction

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.order_repository import OrderRepository
from application.orders.domain_layer.stock.stock import Stock
from application.orders.domain_layer.stock.stock_repository import StockRepository


class Conflict(Exception):
    pass


class PessimisticRebindUseCase:
    def __init__(self, order_repository: OrderRepository, stock_repository: StockRepository,
                 unit_of_work: OrdersUnitOfWork) -> None:
        self._order_repository: OrderRepository = order_repository
        self._stock_repository: StockRepository = stock_repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, customer_id: str, order_id: str, other_id: str, sku: str) -> None:
        # joint-commit: 함께 order×2  잠금 order(order_id)  불변식 옮긴 요청은 정확히 한 주문에만 있다
        with self._unit_of_work:
            first_id, second_id = sorted((order_id, other_id))
            first: Order = self._order_repository.get_for_update(first_id)
            second: Order = self._order_repository.get_for_update(second_id)
            source: Order = first if first.order_id == order_id else second
            target: Order = second if source is first else first
            source.cancel()
            target.move_to(source.order_id)
            self._order_repository.save(source)
            self._order_repository.save(target)
