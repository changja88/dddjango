from application.orders.driven_layer.django_orders.models.order_model import OrderModel

ROUTES: dict = {"order_placed": ["handler_a"]}


def wire_order_events() -> None:
    broker = object()
    broker.subscribe(lambda event: None)
    OrderModel.objects.count()
