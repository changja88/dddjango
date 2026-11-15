from application.orders.driven_layer.django_orders.models import ShipmentModel


class DjangoPackageStarDomainBypassQuery:
    def count(self) -> int:
        return ShipmentModel.objects.filter(status=ShipmentModel.Status.PENDING).count()
