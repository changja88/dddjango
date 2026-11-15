from application.orders.driven_layer.django_orders.models.order_model import STANDARD_RULE, OrderModel


def pending() -> object:
    return OrderModel.objects.all() if STANDARD_RULE.allows(3) and OrderModel.STANDARD_REFUND.allows(3) else None
