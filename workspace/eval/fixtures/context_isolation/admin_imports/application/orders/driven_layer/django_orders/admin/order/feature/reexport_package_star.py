from application.orders.driven_layer.django_orders.models import ShipmentModel


def pending() -> object:
    return ShipmentModel.objects.filter(status=ShipmentModel.Status.PENDING)
