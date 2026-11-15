from application.orders.driven_layer.django_orders.models.order_model import OrderModel


class DjangoClassAliasDomainBypassQuery:
    def count(self) -> int:
        return OrderModel.objects.filter(status=OrderModel.Status.PENDING).count()
