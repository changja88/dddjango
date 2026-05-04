from django.db import models
from django.utils import timezone


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_CANCELLED = "cancelled"
    STATUS_SHIPPED = "shipped"

    customer_email = models.EmailField()
    status = models.CharField(max_length=24, default=STATUS_PENDING)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def cancel(self, reason: str, actor_email: str) -> None:
        if self.status == self.STATUS_SHIPPED:
            raise ValueError("shipped orders cannot be cancelled")
        if self.status == self.STATUS_CANCELLED:
            return
        if not reason:
            raise ValueError("cancel reason is required")
        self.status = self.STATUS_CANCELLED
        self.cancel_reason = f"{reason} by {actor_email}"
        self.cancelled_at = timezone.now()
        self.save(update_fields=["status", "cancel_reason", "cancelled_at"])


class Product(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class Reservation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    idempotency_key = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
