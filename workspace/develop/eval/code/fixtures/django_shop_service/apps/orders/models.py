from __future__ import annotations

from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        CANCELLED = "cancelled", "Cancelled"

    customer_email = models.EmailField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    idempotency_key = models.CharField(max_length=128)
    request_fingerprint = models.CharField(max_length=64)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.CREATED)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["idempotency_key"],
                name="uniq_order_idempotency_key",
            )
        ]

    def __str__(self) -> str:
        return f"Order #{self.pk or 'unsaved'} {self.customer_email}"
