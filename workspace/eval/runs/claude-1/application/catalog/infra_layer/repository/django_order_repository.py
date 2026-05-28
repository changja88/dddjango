"""DjangoOrderRepository — OrderRepository 의 Django ORM 구현(인프라).

도메인 Order를 OrderModel로 변환·저장하고 부여된 PK를 반환한다.
status는 OrderModel default 'CREATED'에 맡긴다(도메인 Order는 status를 모른다 §1.3).
"""
from application.catalog.domain_layer.order.order import Order
from application.catalog.domain_layer.order.repository.order_repository import (
    OrderRepository,
)
from application.catalog.infra_layer.django_catalog.models.order_model import OrderModel


class DjangoOrderRepository(OrderRepository):
    def save(self, order: Order) -> int:
        row = OrderModel.objects.create(
            product_id=order.product_id,
            quantity=order.quantity,
            unit_price=order.unit_price,
            total_price=order.total_price,
        )
        return row.id
