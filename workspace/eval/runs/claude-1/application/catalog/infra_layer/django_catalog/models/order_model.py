"""OrderModel — Order 애그리거트의 ORM 영속 모델(§4.1).

도메인 Order와 분리된 ORM 클래스(<Name>Model 규약). 테이블명 catalog_order.
- FK on_delete=PROTECT — 주문이 가리키는 상품의 임의 삭제로 무결성이 깨지지 않게.
- unit_price/total_price 는 주문 시점 스냅샷.
- CHECK quantity >= 1(I3 영속), total_price = unit_price * quantity(I4 DB 경계 집행).
- status default 'CREATED' — 향후 상태 전이 자리(도메인 전이 없음 §1.3).
"""
from django.db import models

from application.catalog.infra_layer.django_catalog.models.product_model import (
    ProductModel,
)


class OrderModel(models.Model):
    product = models.ForeignKey(
        ProductModel,
        on_delete=models.PROTECT,
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.PositiveIntegerField()
    total_price = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default="CREATED")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "catalog_order"
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gte=1),
                name="catalog_order_quantity_gte_1",
            ),
            models.CheckConstraint(
                check=models.Q(total_price=models.F("unit_price") * models.F("quantity")),
                name="catalog_order_total_price_eq_unit_price_times_quantity",
            ),
        ]
