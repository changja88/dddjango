"""ProductModel — Product 애그리거트의 ORM 영속 모델(§4.1).

도메인 Product와 분리된 ORM 클래스(<Name>Model 규약). 테이블명 catalog_product 보존.
CHECK stock >= 0 으로 음수 재고 영속화를 DB 경계에서 원천 차단(I2 집행).
"""
from django.db import models


class ProductModel(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "catalog_product"
        constraints = [
            models.CheckConstraint(
                check=models.Q(stock__gte=0),
                name="catalog_product_stock_gte_0",
            ),
        ]
