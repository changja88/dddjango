from django.db import connection
from django.db.models import F

from application.catalog.domain_layer.product.product import Product
from application.catalog.domain_layer.product.repository.product_repository import (
    ConcurrentProductUpdate,
    LoadedProduct,
    ProductNotFound,
    ProductRepository,
)
from application.catalog.infra_layer.django_catalog.models import ProductModel


class DjangoProductRepository(ProductRepository):
    def get(self, product_id: int) -> LoadedProduct:
        queryset = ProductModel.objects
        if connection.vendor != "sqlite":
            queryset = queryset.select_for_update()

        try:
            product_model = queryset.get(pk=product_id)
        except ProductModel.DoesNotExist as error:
            raise ProductNotFound(product_id) from error

        return LoadedProduct(
            product=Product(
                id=product_model.id,
                name=product_model.name,
                price=product_model.price,
                stock=product_model.stock,
            ),
            version=product_model.version,
        )

    def save(self, product: Product, expected_version: int) -> None:
        updated_count = ProductModel.objects.filter(
            pk=product.id,
            version=expected_version,
        ).update(
            stock=product.stock,
            version=F("version") + 1,
        )
        if updated_count == 0:
            raise ConcurrentProductUpdate()
