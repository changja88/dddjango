from collections.abc import Callable
from typing import Optional, Protocol, TypeVar

from application.orders.application_layer.create_order.dto.create_order_command import (
    CreateOrderCommand,
    CreateOrderResult,
)
from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.port.product_inventory_port import (
    InventoryConflict,
    ProductInventoryPort,
)
from application.orders.domain_layer.order.repository.order_repository import (
    OrderRepository,
)
from application.orders.domain_layer.order.value_object.quantity import Quantity


ResultT = TypeVar("ResultT")


class TransactionRunner(Protocol):
    def run(self, operation: Callable[[], ResultT]) -> ResultT:
        raise NotImplementedError


class CreateOrderApp:
    def __init__(
        self,
        *,
        order_repository: OrderRepository,
        product_inventory_port: ProductInventoryPort,
        transaction_runner: TransactionRunner,
    ) -> None:
        self._order_repository = order_repository
        self._product_inventory_port = product_inventory_port
        self._transaction_runner = transaction_runner

    def execute(self, command: CreateOrderCommand) -> CreateOrderResult:
        last_conflict: Optional[InventoryConflict] = None
        for _attempt in range(2):
            try:
                return self._transaction_runner.run(lambda: self._execute_once(command))
            except InventoryConflict as exc:
                last_conflict = exc
        raise InventoryConflict("inventory conflict after retry") from last_conflict

    def _execute_once(self, command: CreateOrderCommand) -> CreateOrderResult:
        quantity = Quantity(command.quantity)
        snapshot = self._product_inventory_port.load_snapshot(command.product_id)
        order = Order.create(
            product_id=command.product_id,
            quantity=quantity,
            inventory_snapshot=snapshot,
        )
        self._product_inventory_port.decrement_stock(snapshot, quantity)
        saved_order = self._order_repository.save(order)
        return CreateOrderResult(
            id=saved_order.id or 0,
            product_id=saved_order.product_id,
            quantity=saved_order.quantity,
            status=saved_order.status,
        )
