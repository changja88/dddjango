from application.orders.driven_layer.django_orders.models.order_model import PENDING_VALUE, OrderModel


def pending() -> object:
    return OrderModel.objects.filter(status=PENDING_VALUE)
