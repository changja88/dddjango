from application.catalog.application_layer.create_order.dto.create_order_command import (
    CreateOrderCommand,
)
from application.catalog.application_layer.unit_of_work import CatalogUnitOfWork
from application.catalog.domain_layer.order.entity.order import Order


class CreateOrderApp:
    def __init__(self, unit_of_work: CatalogUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def create(self, command: CreateOrderCommand) -> Order:
        with self._unit_of_work as unit_of_work:
            accepted_stock = unit_of_work.product_repository.accept_stock(
                product_id=command.product_id,
                quantity=command.quantity,
            )
            order = Order(
                product_id=accepted_stock.product_id,
                quantity=accepted_stock.accepted_quantity,
                unit_price=accepted_stock.unit_price,
            )
            created_order = unit_of_work.order_repository.add(order)
            unit_of_work.commit()
            return created_order
