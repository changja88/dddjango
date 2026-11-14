from application.orders.domain_layer.order.order import Order


class PlaceOrderUseCase:
    def execute(self, command) -> None: ...
