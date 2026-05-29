from typing import Any

from django.core.exceptions import ValidationError
from django.db import migrations, models


def ensure_existing_stock_is_nonnegative(apps: Any, schema_editor: Any) -> None:
    product_model = apps.get_model("catalog", "ProductModel")
    if product_model.objects.filter(stock__lt=0).exists():
        raise ValidationError("Cannot add stock constraint while negative stock exists.")


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0002_productmodel_state"),
    ]

    operations = [
        migrations.RunPython(
            ensure_existing_stock_is_nonnegative,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AddField(
            model_name="productmodel",
            name="version",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddConstraint(
            model_name="productmodel",
            constraint=models.CheckConstraint(
                check=models.Q(stock__gte=0),
                name="catalog_product_stock_nonnegative",
            ),
        ),
        migrations.AddConstraint(
            model_name="productmodel",
            constraint=models.CheckConstraint(
                check=models.Q(version__gte=0),
                name="catalog_product_version_nonnegative",
            ),
        ),
    ]
