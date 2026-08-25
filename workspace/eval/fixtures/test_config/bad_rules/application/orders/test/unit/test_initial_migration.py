from importlib import import_module
from types import ModuleType

from django.db import migrations


def test_initial_migration_creates_order_table() -> None:
    module: ModuleType = import_module("application.orders.driven_layer.django_orders.migrations.0001_initial")
    operations: list[object] = list(module.Migration.operations)
    assert any(isinstance(op, migrations.CreateModel) and op.name == "OrderModel" for op in operations)
