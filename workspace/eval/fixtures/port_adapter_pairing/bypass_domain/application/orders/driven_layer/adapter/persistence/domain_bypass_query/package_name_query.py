from application.orders.driven_layer.django_orders.models import Kind, OrderModel


class DjangoPackageNameDomainBypassQuery:
    def count(self) -> int:
        return OrderModel.objects.filter(status=Kind.PENDING).count()
