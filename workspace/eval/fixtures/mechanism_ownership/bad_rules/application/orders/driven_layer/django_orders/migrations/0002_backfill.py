from django.db import migrations

from application.orders.domain_layer.order.order import Order


def backfill(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("orders", "0001_initial")]

    operations = [
        migrations.RunPython(backfill),
    ]

    atomic = False
