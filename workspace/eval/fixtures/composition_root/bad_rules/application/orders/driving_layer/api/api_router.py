from config.api import api
from application.orders.driving_layer.api.order.order_controller import OrderController

PREFIX: str = "/orders"


def register_orders_api(api) -> None:
    api.register_controllers(OrderController)


def register_admin_api(api) -> None:
    pass


api.register_controllers(OrderController)
