from application.orders.driven_layer.django_orders.models import OrderModel


class DjangoPackageDerivedValueDomainBypassQuery:
    def count(self) -> int:
        return OrderModel.objects.filter(status=OrderModel.STATUS_PENDING).count()
