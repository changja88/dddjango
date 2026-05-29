"""DjangoOrderRepository ↔ 실제 DB 통합 테스트 (명세 §4.1).

리포지토리가 도메인 Order 를 OrderModel 로 영속화하고, 식별자가 부여된 Order 를
돌려주는지 검증한다.
"""
from datetime import datetime, timezone

from django.test import TestCase

from application.ordering.domain_layer.order.order import Order, OrderStatus
from application.ordering.domain_layer.order.value_object.quantity import Quantity
from application.ordering.infra_layer.django_ordering.models import OrderModel
from application.ordering.infra_layer.repository.order_repository import (
    DjangoOrderRepository,
)


class DjangoOrderRepositoryTest(TestCase):
    def test_add_persists_order_and_assigns_id(self) -> None:
        repository = DjangoOrderRepository()
        order = Order.place(
            product_id=42,
            quantity=Quantity(3),
            unit_price=1000,
            now=datetime(2026, 5, 29, tzinfo=timezone.utc),
        )

        persisted = repository.add(order)

        self.assertIsNotNone(persisted.id)
        row = OrderModel.objects.get(pk=persisted.id)
        self.assertEqual(row.product_id, 42)
        self.assertEqual(row.quantity, 3)
        self.assertEqual(row.unit_price, 1000)
        self.assertEqual(row.total_price, 3000)
        self.assertEqual(row.status, OrderStatus.PLACED.value)
