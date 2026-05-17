from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("customer_email", models.EmailField(max_length=254)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("idempotency_key", models.CharField(max_length=128)),
                ("request_fingerprint", models.CharField(max_length=64)),
                (
                    "status",
                    models.CharField(
                        choices=[("created", "Created"), ("cancelled", "Cancelled")],
                        default="created",
                        max_length=24,
                    ),
                ),
                ("note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddConstraint(
            model_name="order",
            constraint=models.UniqueConstraint(
                fields=("idempotency_key",),
                name="uniq_order_idempotency_key",
            ),
        ),
    ]
