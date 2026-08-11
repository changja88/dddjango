from __future__ import annotations

from application.orders.domain_layer.ledger.ledger_repository import LedgerRepository
from application.orders.domain_layer.order.event.order_placed import OrderPlaced
from application.orders.domain_layer.order.order_repository import OrderRepository


class PlaceOrderUseCase:
    def __init__(self, order_repository: OrderRepository, ledger_repository: LedgerRepository) -> None:
        self._order_repository: OrderRepository = order_repository
        self._ledger_repository: LedgerRepository = ledger_repository

    def execute(self, order_id: str) -> None:
        order = self._order_repository.get(order_id)
        order.lines.append(order_id)
        fact = OrderPlaced(order_id=order_id)
        self._order_repository.save(order)
        self._ledger_repository.save(fact)
        rows = self._order_repository.list_open()
        self._order_repository.save_all(rows)
