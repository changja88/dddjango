from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.repository.order_repository import (
    OrderRepository,
)
from application.orders.infra_layer.django_orders.models import OrderModel


class DjangoOrderRepository(OrderRepository):
    def save(self, order: Order) -> Order:
        order_model = OrderModel.objects.create(
            product_id=order.product_id,
            quantity=order.quantity,
            status=order.status,
        )
        return Order(
            id=order_model.id,
            product_id=order_model.product_id,
            quantity=order_model.quantity,
            status=order_model.status,
            created_at=order_model.created_at,
        )
