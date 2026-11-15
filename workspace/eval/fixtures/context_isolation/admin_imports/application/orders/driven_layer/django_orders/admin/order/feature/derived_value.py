from application.orders.driven_layer.django_orders.models.order_model import OrderModel


def pending() -> object:
    return OrderModel.objects.filter(status__in=[OrderModel.STATUS_PENDING, OrderModel.STATUS_SHIPPED, OrderModel.STATUS_PLAIN])
