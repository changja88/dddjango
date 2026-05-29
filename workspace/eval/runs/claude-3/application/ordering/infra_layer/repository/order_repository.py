"""DjangoOrderRepository — OrderRepository 의 Django ORM 구현 (명세 §4.2).

도메인 Order 를 OrderModel 로 매핑해 영속화한다. catalog 모델을 import 하지
않는다(ACL 책임 — 명세 §1.4 분리).
"""
from application.ordering.domain_layer.order.order import Order
from application.ordering.domain_layer.order.repository.order_repository import (
    OrderRepository,
)
from application.ordering.infra_layer.django_ordering.models import OrderModel


class DjangoOrderRepository(OrderRepository):
    def add(self, order: Order) -> Order:
        row = OrderModel.objects.create(
            product_id=order.product_id,
            quantity=order.quantity.value,
            unit_price=order.unit_price,
            total_price=order.total_price,
            status=order.status.value,
        )
        order.assign_id(row.pk)
        return order
