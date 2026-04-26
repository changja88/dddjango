from django.conf import settings
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "결제 대기"
        PAID = "paid", "결제 완료"
        SHIPPED = "shipped", "배송 중"
        DELIVERED = "delivered", "배송 완료"
        CANCELLED = "cancelled", "취소"

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="주문자",
    )
    status = models.CharField(
        "상태",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    total_amount = models.DecimalField(
        "총액", max_digits=12, decimal_places=2, default=0
    )
    ordered_at = models.DateTimeField("주문일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        ordering = ["-ordered_at"]
        verbose_name = "주문"
        verbose_name_plural = "주문 목록"

    def __str__(self):
        return f"주문 #{self.pk} - {self.buyer}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="주문",
    )
    book = models.ForeignKey(
        "books.Book",
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="도서",
    )
    quantity = models.PositiveIntegerField("수량", default=1)
    unit_price = models.DecimalField(
        "단가", max_digits=10, decimal_places=2
    )

    class Meta:
        verbose_name = "주문 항목"
        verbose_name_plural = "주문 항목 목록"

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
