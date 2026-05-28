import django.db.models.deletion
from django.apps.registry import Apps
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def validate_product_non_negative_values(
    apps: Apps,
    schema_editor: BaseDatabaseSchemaEditor,
) -> None:
    product = apps.get_model("catalog", "Product")
    invalid_rows_exist = product.objects.filter(
        models.Q(price__lt=0) | models.Q(stock__lt=0)
    ).exists()
    if invalid_rows_exist:
        raise RuntimeError(
            "catalog_product contains negative price or stock values; "
            "clean the data before applying catalog constraints."
        )


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            validate_product_non_negative_values,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.CheckConstraint(
                check=models.Q(("price__gte", 0)),
                name="catalog_product_price_gte_0",
            ),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.CheckConstraint(
                check=models.Q(("stock__gte", 0)),
                name="catalog_product_stock_gte_0",
            ),
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameModel(
                    old_name="Product",
                    new_name="ProductModel",
                ),
                migrations.AlterModelTable(
                    name="ProductModel",
                    table="catalog_product",
                ),
            ],
        ),
        migrations.CreateModel(
            name="OrderModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField()),
                ("unit_price", models.PositiveIntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="orders",
                        to="catalog.productmodel",
                    ),
                ),
            ],
            options={
                "db_table": "catalog_order",
            },
        ),
        migrations.AddConstraint(
            model_name="ordermodel",
            constraint=models.CheckConstraint(
                check=models.Q(("quantity__gt", 0)),
                name="catalog_order_quantity_gt_0",
            ),
        ),
        migrations.AddConstraint(
            model_name="ordermodel",
            constraint=models.CheckConstraint(
                check=models.Q(("unit_price__gte", 0)),
                name="catalog_order_unit_price_gte_0",
            ),
        ),
    ]
