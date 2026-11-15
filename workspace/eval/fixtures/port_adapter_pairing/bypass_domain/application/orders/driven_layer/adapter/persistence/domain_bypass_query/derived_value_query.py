from application.orders.driven_layer.django_orders.models.order_model import PENDING_VALUE, OrderModel


class DjangoDerivedValueDomainBypassQuery:
    def count(self) -> int:
        return OrderModel.objects.filter(status__in=[OrderModel.STATUS_PENDING, PENDING_VALUE, OrderModel.STATUS_SHIPPED, OrderModel.STATUS_PLAIN]).count()
