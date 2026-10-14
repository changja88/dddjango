from application.orders.application_layer.order.close_order.close_order_command import CloseOrderCommand
from application.orders.application_layer.order.close_order.close_order_result import CloseOrderResult
from application.orders.domain_layer.order.order_repository import OrderRepository


class CloseOrderUseCase:
    def __init__(self, *, order_repository: OrderRepository) -> None:
        self._order_repository = order_repository

    def execute(self, command: CloseOrderCommand) -> CloseOrderResult:
        order = self._order_repository.get_for_update(command.order_id)
        order.rename(command.note)
        self._order_repository.save(order)
        return CloseOrderResult(order_id=command.order_id)
