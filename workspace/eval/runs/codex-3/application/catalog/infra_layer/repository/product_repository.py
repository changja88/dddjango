from django.db.models import F

from application.catalog.domain_layer.product.exception import (
    InsufficientStock,
    ProductNotFound,
)
from application.catalog.domain_layer.product.value_object.accepted_stock import (
    AcceptedStock,
)
from application.catalog.infra_layer.django_catalog.models.product_model import (
    ProductModel,
)


class DjangoProductRepository:
    def accept_stock(self, product_id: int, quantity: int) -> AcceptedStock:
        if type(product_id) is not int or product_id <= 0:
            raise ValueError("product_id must be a positive integer.")
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("quantity must be a positive integer.")

        updated_rows = (
            ProductModel.objects.filter(id=product_id, stock__gte=quantity)
            .update(stock=F("stock") - quantity)
        )
        if updated_rows == 1:
            product = ProductModel.objects.only("price").get(id=product_id)
            return AcceptedStock(
                product_id=product_id,
                accepted_quantity=quantity,
                unit_price=product.price,
            )

        if ProductModel.objects.filter(id=product_id).exists():
            raise InsufficientStock()
        raise ProductNotFound()
