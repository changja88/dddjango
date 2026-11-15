from application.orders.driven_layer.django_orders.models.order_model import Kind, OrderModel


class DjangoReexportNameDomainBypassQuery:
    def count(self) -> int:
        return OrderModel.objects.filter(status=Kind.PENDING).count()
