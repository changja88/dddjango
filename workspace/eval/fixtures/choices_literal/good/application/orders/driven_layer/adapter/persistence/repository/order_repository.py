from application.orders.driven_layer.django_orders.models.order_model import OrderModel, OrderStatus


class DjangoOrderRepository:
    def pending(self):
        return OrderModel.objects.filter(status=OrderStatus.PENDING)
