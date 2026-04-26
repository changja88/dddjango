from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class OrderItem(models.Model):
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name="items",
    )
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gte=1),
                name="orderitem_quantity_positive",
            ),
            models.CheckConstraint(
                check=models.Q(unit_price__gt=Decimal("0")),
                name="orderitem_unit_price_positive",
            ),
        ]

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"


class OrderQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)

    def pending(self):
        return self.filter(status=Order.Status.PENDING)


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        db_default=Decimal("0"),
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
        db_default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_amount__gte=Decimal("0")),
                name="order_total_amount_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(
                    status__in=[s.value for s in Status]
                ),
                name="order_status_valid",
            ),
        ]

    def __str__(self):
        return f"Order #{self.pk} ({self.get_status_display()})"

    def clean(self):
        if self.status == self.Status.CONFIRMED and self.total_amount <= 0:
            raise ValidationError(
                {"total_amount": "Confirmed orders must have a positive total."}
            )

    def confirm(self):
        if self.status != self.Status.PENDING:
            raise ValidationError("Only pending orders can be confirmed.")
        self.status = self.Status.CONFIRMED
        self.save(update_fields=["status", "updated_at"])

    def cancel(self):
        if self.status != self.Status.PENDING:
            raise ValidationError("Only pending orders can be cancelled.")
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "updated_at"])
