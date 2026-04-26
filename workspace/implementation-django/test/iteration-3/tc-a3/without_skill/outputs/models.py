"""
Inventory model for Django 5.2 LTS.

Django 5.2 features used:
- db_default: DB-level default for last_received_at (Now())
- CheckConstraint with condition alias (Django 5.1+)
- GeneratedField for computed available_quantity (Django 5.0+)
"""

from django.db import models
from django.db.models import F
from django.db.models.functions import Now


class Inventory(models.Model):
    """상품 재고 모델: 특정 창고 내 상품의 입출고 수량을 관리한다."""

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="inventories",
        verbose_name="상품",
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.PROTECT,
        related_name="inventories",
        verbose_name="창고",
    )

    quantity_received = models.PositiveIntegerField(
        verbose_name="입고 수량",
        default=0,
    )
    quantity_shipped = models.PositiveIntegerField(
        verbose_name="출고 수량",
        default=0,
    )

    # Django 5.0+ GeneratedField — DB가 직접 계산하는 가상 컬럼
    available_quantity = models.GeneratedField(
        expression=F("quantity_received") - F("quantity_shipped"),
        output_field=models.IntegerField(verbose_name="가용 재고"),
        db_persist=True,
    )

    # Django 5.2 db_default — Python이 아닌 DB에서 기본값을 계산
    last_received_at = models.DateTimeField(
        verbose_name="최종 입고일",
        db_default=Now(),
    )

    class Meta:
        verbose_name = "재고"
        verbose_name_plural = "재고 목록"

        constraints = [
            # 같은 상품 + 같은 창고 조합은 고유
            models.UniqueConstraint(
                fields=["product", "warehouse"],
                name="uq_inventory_product_warehouse",
            ),
            # 가용 재고(입고 - 출고)가 음수가 되면 안 됨
            models.CheckConstraint(
                condition=models.Q(quantity_received__gte=F("quantity_shipped")),
                name="ck_inventory_available_not_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.product} @ {self.warehouse} (가용: {self.available_quantity})"
