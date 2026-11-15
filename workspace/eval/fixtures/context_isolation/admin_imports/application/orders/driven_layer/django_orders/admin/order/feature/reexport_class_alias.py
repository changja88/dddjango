from application.orders.driven_layer.django_orders.models.order_model import OrderModel


def pending() -> object:
    return OrderModel.objects.filter(status=OrderModel.Status.PENDING)
