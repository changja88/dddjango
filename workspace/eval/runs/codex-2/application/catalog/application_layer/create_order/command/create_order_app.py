from typing import Callable, ContextManager

from django.db import transaction

from application.catalog.application_layer.create_order.dto.create_order_command import (
    CreateOrderCommand,
)
from application.catalog.application_layer.create_order.dto.create_order_result import (
    CreateOrderResult,
)
from application.catalog.domain_layer.order.order import Order
from application.catalog.domain_layer.order.repository.order_repository import OrderRepository
from application.catalog.domain_layer.product.exception import InvalidReserveQuantity
from application.catalog.domain_layer.product.repository.product_repository import (
    ProductRepository,
)


class CreateOrderApp:
    def __init__(
        self,
        *,
        product_repository: ProductRepository,
        order_repository: OrderRepository,
        transaction_factory: Callable[[], ContextManager[None]] = transaction.atomic,
    ) -> None:
        self.product_repository = product_repository
        self.order_repository = order_repository
        self.transaction_factory = transaction_factory

    def create(self, command: CreateOrderCommand) -> CreateOrderResult:
        if command.quantity < 1:
            raise InvalidReserveQuantity(command.quantity)

        with self.transaction_factory():
            product_id, unit_price, remaining_stock = self.product_repository.reserve(
                command.product_id,
                command.quantity,
            )
            order = Order.create(
                product_id=product_id,
                quantity=command.quantity,
                unit_price=unit_price,
            )
            order_id = self.order_repository.save(order)

        return CreateOrderResult(
            order_id=order_id,
            product_id=product_id,
            quantity=order.quantity,
            unit_price=order.unit_price,
            total_price=order.total_price,
            remaining_stock=remaining_stock,
        )

