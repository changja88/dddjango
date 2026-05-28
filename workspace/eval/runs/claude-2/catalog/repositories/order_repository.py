"""DjangoOrderRepository — Order 저장(ORM<->도메인 Data Mapper, 설계 명세 section 4)."""

from __future__ import annotations

from catalog.domain.order import Order
from catalog.domain.order_repository import OrderRepository
from catalog.models import OrderModel


class DjangoOrderRepository(OrderRepository):
    def add(self, order: Order) -> Order:
        row = OrderModel.objects.create(
            product_id=order.product_id,
            quantity=order.quantity,
            status=order.status,
        )
        order.id = row.id
        return order
