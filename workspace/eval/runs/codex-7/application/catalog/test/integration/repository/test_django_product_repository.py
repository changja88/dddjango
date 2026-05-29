from django.test import TestCase

from application.catalog.domain_layer.product.product import Product
from application.catalog.domain_layer.product.repository.product_repository import (
    ConcurrentProductUpdate,
)
from application.catalog.infra_layer.django_catalog.models import ProductModel
from application.catalog.infra_layer.repository.product_repository import (
    DjangoProductRepository,
)


class DjangoProductRepositoryTests(TestCase):
    def test_loads_product_with_optimistic_concurrency_token(self):
        product_model = ProductModel.objects.create(
            name="Widget",
            price=1000,
            stock=10,
            version=2,
        )
        repository = DjangoProductRepository()

        loaded_product = repository.get(product_model.id)

        self.assertEqual(loaded_product.product.id, product_model.id)
        self.assertEqual(loaded_product.product.stock, 10)
        self.assertEqual(loaded_product.version, 2)

    def test_save_updates_stock_and_increments_version_with_expected_token(self):
        product_model = ProductModel.objects.create(
            name="Widget",
            price=1000,
            stock=10,
            version=0,
        )
        repository = DjangoProductRepository()

        repository.save(
            Product(id=product_model.id, name="Widget", price=1000, stock=7),
            expected_version=0,
        )

        product_model.refresh_from_db()
        self.assertEqual(product_model.stock, 7)
        self.assertEqual(product_model.version, 1)

    def test_save_rejects_stale_expected_token(self):
        product_model = ProductModel.objects.create(
            name="Widget",
            price=1000,
            stock=10,
            version=1,
        )
        repository = DjangoProductRepository()

        with self.assertRaises(ConcurrentProductUpdate):
            repository.save(
                Product(id=product_model.id, name="Widget", price=1000, stock=7),
                expected_version=0,
            )

        product_model.refresh_from_db()
        self.assertEqual(product_model.stock, 10)
        self.assertEqual(product_model.version, 1)
