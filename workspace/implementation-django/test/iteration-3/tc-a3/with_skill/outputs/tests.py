from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from apps.products.factories import ProductFactory
from apps.warehouses.factories import WarehouseFactory

from .models import Inventory


class InventoryModelTests(TestCase):
    def setUp(self):
        self.product = ProductFactory()
        self.warehouse = WarehouseFactory()
        self.inventory = Inventory.objects.create(
            product=self.product,
            warehouse=self.warehouse,
            quantity_received=100,
            quantity_shipped=30,
        )

    def test_available_stock_is_auto_calculated(self):
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.available_stock, 70)

    def test_unique_product_warehouse_constraint(self):
        with self.assertRaises(IntegrityError):
            Inventory.objects.create(
                product=self.product,
                warehouse=self.warehouse,
                quantity_received=50,
                quantity_shipped=0,
            )

    def test_negative_stock_raises_db_constraint(self):
        with self.assertRaises(IntegrityError):
            Inventory.objects.create(
                product=ProductFactory(),
                warehouse=self.warehouse,
                quantity_received=10,
                quantity_shipped=20,
            )

    def test_clean_validates_negative_stock(self):
        inventory = Inventory(
            product=ProductFactory(),
            warehouse=self.warehouse,
            quantity_received=10,
            quantity_shipped=20,
        )
        with self.assertRaises(ValidationError) as ctx:
            inventory.clean()
        self.assertIn("quantity_shipped", ctx.exception.message_dict)

    def test_receive_increases_quantity(self):
        self.inventory.receive(50)
        self.assertEqual(self.inventory.quantity_received, 150)
        self.assertEqual(self.inventory.available_stock, 120)

    def test_ship_decreases_available_stock(self):
        self.inventory.ship(20)
        self.assertEqual(self.inventory.quantity_shipped, 50)
        self.assertEqual(self.inventory.available_stock, 50)

    def test_ship_raises_when_insufficient_stock(self):
        with self.assertRaises(ValidationError):
            self.inventory.ship(200)

    def test_str_representation(self):
        result = str(self.inventory)
        self.assertIn("@", result)

    def test_last_received_at_has_db_default(self):
        inventory = Inventory.objects.create(
            product=ProductFactory(),
            warehouse=WarehouseFactory(),
            quantity_received=10,
            quantity_shipped=0,
        )
        inventory.refresh_from_db()
        self.assertIsNotNone(inventory.last_received_at)
