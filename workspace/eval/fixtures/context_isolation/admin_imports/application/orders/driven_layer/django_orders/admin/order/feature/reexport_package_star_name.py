from application.orders.driven_layer.django_orders.models import OrderStatus


def pending() -> object:
    return OrderStatus.PENDING
