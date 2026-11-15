from application.orders.driven_layer.django_orders.models.order_model import OrderModel

from .open_statuses import OPEN


class DjangoPromotedPartDomainBypassQuery:
    def count(self) -> int:
        return OrderModel.objects.filter(status__in=OPEN).count()
