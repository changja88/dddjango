from application.catalog.domain_layer.order.entity.order import Order
from application.catalog.infra_layer.django_catalog.models.order_model import OrderModel


class DjangoOrderRepository:
    def add(self, order: Order) -> Order:
        order_model = OrderModel.objects.create(
            product_id=order.product_id,
            quantity=order.quantity,
            unit_price=order.unit_price,
        )
        return Order(
            id=order_model.id,
            product_id=order_model.product_id,
            quantity=order_model.quantity,
            unit_price=order_model.unit_price,
            created_at=order_model.created_at,
        )
