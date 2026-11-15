from application.orders.driven_layer.django_orders.models import OrderModel


class DjangoPackageClassAliasDomainBypassQuery:
    def count(self) -> int:
        return OrderModel.objects.filter(status=OrderModel.Status.PENDING).count()
