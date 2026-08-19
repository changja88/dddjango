from application.orders.driving_layer.api.order.order_controller import OrderController


def register_orders_api(api) -> None:
    api.register_controllers(OrderController)
