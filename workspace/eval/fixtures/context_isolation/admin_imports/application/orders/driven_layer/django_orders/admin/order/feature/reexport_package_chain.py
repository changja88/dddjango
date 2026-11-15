from application.orders.driven_layer.django_orders import models as mm


def pending() -> object:
    return mm.order_model.OrderModel.objects.filter(status=mm.order_model.OrderModel.Status.PENDING)
