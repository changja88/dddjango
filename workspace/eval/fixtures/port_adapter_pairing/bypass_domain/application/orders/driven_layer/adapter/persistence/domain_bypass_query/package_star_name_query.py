from application.orders.driven_layer.django_orders.models import OrderStatus, ShipmentModel


class DjangoPackageStarNameDomainBypassQuery:
    def count(self) -> int:
        return ShipmentModel.objects.filter(status=OrderStatus.PENDING).count()
