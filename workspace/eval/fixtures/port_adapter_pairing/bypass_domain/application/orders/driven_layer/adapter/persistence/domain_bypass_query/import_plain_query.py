import application.orders.domain_layer.order.value_object.order_status as order_status

from application.orders.driven_layer.django_orders.models.order_model import OrderModel


class DjangoImportPlainDomainBypassQuery:
    def count(self) -> int:
        return OrderModel.objects.filter(status=order_status.OrderStatus.PENDING).count()
