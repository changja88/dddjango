from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)


class OrderModel(models.Model):
    """단일 품목 주문의 ORM 모델(설계 명세 section 3.1).

    도메인 Order와 구분하기 위해 클래스명에 Model 접미사를 붙인다.
    """

    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="orders"
    )
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=16, default="CREATED")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gte=1),
                name="order_quantity_gte_1",
            ),
            models.CheckConstraint(
                check=models.Q(status="CREATED"),
                name="order_status_created",
            ),
        ]
