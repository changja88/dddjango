from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameModel(
                    old_name="Product",
                    new_name="ProductModel",
                ),
                migrations.AlterModelTable(
                    name="productmodel",
                    table="catalog_product",
                ),
            ],
        ),
    ]

