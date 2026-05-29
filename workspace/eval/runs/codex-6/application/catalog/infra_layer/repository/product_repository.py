from typing import Optional

from django.db import transaction

from application.catalog.domain_layer.product.product import Product
from application.catalog.domain_layer.product.repository.product_repository import (
    ProductRepository,
)
from catalog.models import Product as ProductModel


class DjangoProductRepository(ProductRepository):
    def get(self, product_id: int) -> Optional[Product]:
        product_model = (
            ProductModel.objects.filter(pk=product_id)
            .values("id", "stock", "version")
            .first()
        )
        if product_model is None:
            return None

        return Product(
            id=product_model["id"],
            stock=product_model["stock"],
            version=product_model["version"],
        )

    def save(self, product: Product) -> bool:
        with transaction.atomic():
            updated_count = ProductModel.objects.filter(
                pk=product.id,
                version=product.version,
            ).update(
                stock=product.stock,
                version=product.version + 1,
            )

        if updated_count == 1:
            product.version += 1
            return True

        return False
