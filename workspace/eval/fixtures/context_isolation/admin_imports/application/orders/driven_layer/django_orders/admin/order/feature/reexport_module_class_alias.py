from application.orders.driven_layer.django_orders.models import order_model as m


def pending() -> object:
    return m.OrderModel.objects.filter(status=m.OrderModel.Status.PENDING)
