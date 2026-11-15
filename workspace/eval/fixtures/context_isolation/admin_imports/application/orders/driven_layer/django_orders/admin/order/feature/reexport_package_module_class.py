from application.orders.driven_layer.django_orders import models as mm


def pending() -> object:
    return mm.OrderModel.objects.filter(status=mm.OrderModel.Status.PENDING)
