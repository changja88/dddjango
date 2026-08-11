from application.orders.application_layer.order.ship_order.ship_order_command import ShipOrderCommand
from application.orders.application_layer.order.ship_order.helper import calc


class OrderUseCase:
    def execute(self, a: str, b: int) -> dict:
        if a.owner.grade == "vip":
            return {}
        return {}


class OrderPresenter:
    pass
