from application.orders.driven_layer.django_orders.models.order_model import STANDARD_RULE, OrderModel


class DjangoPolicyValueDomainBypassQuery:
    def count(self) -> int:
        return OrderModel.objects.count() if STANDARD_RULE.allows(3) and OrderModel.STANDARD_REFUND.allows(3) else 0
