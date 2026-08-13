from application.orders.application_layer.order.place_order.place_order_command import PlaceOrderCommand
from application.orders.application_layer.order.place_order.place_order_result import PlaceOrderResult


class PlaceOrderUseCase:
    def execute(self, command: PlaceOrderCommand) -> PlaceOrderResult:
        order = self._repository.get(command.order_id)
        order.place()
        events = order.pull_events()
        self._repository.save(order)
        integration_events: list = [self._translate(e) for e in events]
        self._uow.after_commit(self._broker.publish, integration_events)
        return PlaceOrderResult(order_id=command.order_id, total="0")
