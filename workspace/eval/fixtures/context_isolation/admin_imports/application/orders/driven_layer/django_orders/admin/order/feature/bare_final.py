from application.orders.driven_layer.django_orders.models.order_model import BARE_PENDING, OrderModel


def pending() -> object:
    return OrderModel.objects.filter(status=BARE_PENDING)
