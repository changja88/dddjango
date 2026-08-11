from application.orders.driven_layer.django_orders.models.order_model import OrderModel


class DjangoOrderRepository:
    def pending(self):
        return OrderModel.objects.filter(status="pending")

    def settled(self):
        return OrderModel.objects.exclude(status__in=["paid", "refunded"])
