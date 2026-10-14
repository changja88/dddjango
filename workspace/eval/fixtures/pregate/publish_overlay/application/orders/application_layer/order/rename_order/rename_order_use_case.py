from application.orders.application_layer.order.rename_order.rename_order_command import RenameOrderCommand
from application.orders.application_layer.order.rename_order.rename_order_result import RenameOrderResult
from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.order.order_repository import OrderRepository


class RenameOrderUseCase:
    def __init__(self, *, unit_of_work: OrdersUnitOfWork, order_repository: OrderRepository) -> None:
        self._unit_of_work = unit_of_work
        self._order_repository = order_repository

    def execute(self, command: RenameOrderCommand) -> RenameOrderResult:
        with self._unit_of_work:
            order = self._order_repository.get_for_update(command.order_id)
            order.rename(command.note)
            self._order_repository.save(order)
        return RenameOrderResult(order_id=command.order_id)
