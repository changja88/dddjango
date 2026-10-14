from application.orders.application_layer.order.archive_order.archive_order_command import ArchiveOrderCommand
from application.orders.application_layer.order.archive_order.archive_order_result import ArchiveOrderResult
from application.orders.domain_layer.order.order_repository import OrderRepository


class ArchiveOrderUseCase:
    def __init__(self, *, order_repository: OrderRepository) -> None:
        self._order_repository = order_repository

    def execute(self, command: ArchiveOrderCommand) -> ArchiveOrderResult:
        order = self._order_repository.get_for_update(command.order_id)
        order.rename(command.note)
        self._order_repository.save(order)
        return ArchiveOrderResult(order_id=command.order_id)
