from application.orders.driven_layer.django_orders.models.order_model import OrderModel


class DjangoModelOnlyDomainBypassQuery:
    def count(self) -> int:
        return OrderModel.objects.count()
