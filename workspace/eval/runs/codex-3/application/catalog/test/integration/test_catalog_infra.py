from importlib import import_module

from django.db import connection
from django.test import TransactionTestCase

from application.catalog.domain_layer.order.entity.order import Order
from application.catalog.domain_layer.product.exception import InsufficientStock
from application.catalog.infra_layer.django_catalog.models.product_model import (
    ProductModel,
)
from application.catalog.infra_layer.repository.catalog_unit_of_work import (
    DjangoCatalogUnitOfWork,
)
from application.catalog.infra_layer.repository.product_repository import (
    DjangoProductRepository,
)


class CatalogInfrastructureTests(TransactionTestCase):
    reset_sequences = True

    def test_unit_of_work_rolls_back_when_context_exits_without_commit(self):
        product = ProductModel.objects.create(name="Rollback product", price=1000, stock=5)

        with DjangoCatalogUnitOfWork() as unit_of_work:
            unit_of_work.order_repository.add(
                Order(product_id=product.id, quantity=1, unit_price=1000)
            )

        self.assertEqual(self.order_count(), 0)

    def test_unit_of_work_persists_when_commit_is_called(self):
        product = ProductModel.objects.create(name="Commit product", price=1000, stock=5)

        with DjangoCatalogUnitOfWork() as unit_of_work:
            unit_of_work.order_repository.add(
                Order(product_id=product.id, quantity=1, unit_price=1000)
            )
            unit_of_work.commit()

        self.assertEqual(self.order_count(), 1)

    def test_product_repository_rejects_negative_quantity_without_increasing_stock(self):
        product = ProductModel.objects.create(name="Repository product", price=1000, stock=5)
        repository = DjangoProductRepository()

        with self.assertRaises(ValueError):
            repository.accept_stock(product_id=product.id, quantity=-2)

        product.refresh_from_db()
        self.assertEqual(product.stock, 5)

    def test_product_repository_rejects_zero_quantity(self):
        product = ProductModel.objects.create(name="Repository product", price=1000, stock=5)
        repository = DjangoProductRepository()

        with self.assertRaises(ValueError):
            repository.accept_stock(product_id=product.id, quantity=0)

        product.refresh_from_db()
        self.assertEqual(product.stock, 5)

    def test_catalog_models_import_is_safe_compatibility_shim(self):
        legacy_models = import_module("catalog.models")

        self.assertIs(legacy_models.Product, ProductModel)

    def test_product_repository_still_maps_insufficient_stock(self):
        product = ProductModel.objects.create(name="Repository product", price=1000, stock=1)
        repository = DjangoProductRepository()

        with self.assertRaises(InsufficientStock):
            repository.accept_stock(product_id=product.id, quantity=2)

    def order_count(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM catalog_order")
            row = cursor.fetchone()
        return row[0]
