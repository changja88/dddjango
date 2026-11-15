from application.orders.driven_layer.django_orders.models.order_model import OrderModel


class DjangoLocalRelativeDomainBypassQuery:
    def count(self) -> int:
        from ....domain_layer.order.value_object.order_status import OrderStatus
        return OrderModel.objects.filter(status=OrderStatus.PENDING).count()
