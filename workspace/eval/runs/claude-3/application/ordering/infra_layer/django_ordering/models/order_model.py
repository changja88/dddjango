"""OrderModel — 주문 영속화 ORM 모델 (명세 §3.1).

클래스명은 <Name>Model 규약(명세 §0 불변식6). 도메인 애그리거트 Order 와
이름이 충돌하지 않도록 한다. product_id 는 BC 독립을 위해 FK·인덱스 없는
정수 컬럼(OD-3 G1 확정). quantity CHECK 는 수량 불변식의 DB 백스톱이다
(정본은 Quantity VO — 명세 §1.1).
"""
from django.db import models


class OrderModel(models.Model):
    product_id = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    unit_price = models.PositiveIntegerField()
    total_price = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=[("PLACED", "PLACED")], default="PLACED")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "ordering"
        db_table = "ordering_order"
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gte=1),
                name="ordering_order_quantity_gte_1",
            ),
        ]
