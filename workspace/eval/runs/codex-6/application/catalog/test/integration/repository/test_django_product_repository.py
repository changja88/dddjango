from decimal import Decimal

from django.test import TestCase

from application.catalog.domain_layer.product.product import Product
from application.catalog.infra_layer.repository.product_repository import (
    DjangoProductRepository,
)
from catalog.models import Product as ProductModel


class DjangoProductRepositoryTests(TestCase):
    def create_product_model(self, stock: int) -> ProductModel:
        return ProductModel.objects.create(
            name="Widget",
            price=Decimal("12.99"),
            stock=stock,
        )

    def test_get_maps_orm_model_to_domain_product(self) -> None:
        product_model = self.create_product_model(stock=5)
        repository = DjangoProductRepository()

        product = repository.get(product_model.pk)

        self.assertEqual(product, Product(id=product_model.pk, stock=5, version=0))

    def test_save_uses_version_cas_and_increments_version_on_success(self) -> None:
        product_model = self.create_product_model(stock=5)
        repository = DjangoProductRepository()
        product = Product(id=product_model.pk, stock=3, version=0)

        saved = repository.save(product)

        self.assertTrue(saved)
        reloaded = ProductModel.objects.get(pk=product_model.pk)
        self.assertEqual(reloaded.stock, 3)
        self.assertEqual(reloaded.version, 1)

    def test_save_returns_false_for_stale_version_without_overwriting_stock(self) -> None:
        product_model = self.create_product_model(stock=5)
        repository = DjangoProductRepository()
        first_snapshot = repository.get(product_model.pk)
        second_snapshot = repository.get(product_model.pk)

        first_snapshot.reserve(2)
        first_saved = repository.save(first_snapshot)
        second_snapshot.reserve(1)
        second_saved = repository.save(second_snapshot)

        reloaded = ProductModel.objects.get(pk=product_model.pk)
        self.assertTrue(first_saved)
        self.assertFalse(second_saved)
        self.assertEqual(reloaded.stock, 3)
        self.assertEqual(reloaded.version, 1)
