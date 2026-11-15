from application.orders.driven_layer.django_orders.models import OrderModel


def pending() -> object:
    return OrderModel.objects.filter(status=OrderModel.STATUS_PENDING)
