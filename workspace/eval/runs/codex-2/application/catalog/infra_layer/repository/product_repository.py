from django.db import OperationalError
from django.db.models import F

from application.catalog.domain_layer.product.exception import (
    DatabaseBusy,
    InsufficientStock,
    ProductNotFound,
)
from application.catalog.infra_layer.django_catalog.models.product_model import ProductModel


class DjangoProductRepository:
    def reserve(self, product_id: int, quantity: int) -> tuple[int, int, int]:
        try:
            return self._reserve(product_id, quantity)
        except OperationalError as exc:
            if _is_database_busy(exc):
                raise DatabaseBusy("Database is temporarily busy.") from exc
            raise

    def _reserve(self, product_id: int, quantity: int) -> tuple[int, int, int]:
        updated_count = ProductModel.objects.filter(
            pk=product_id,
            stock__gte=quantity,
        ).update(stock=F("stock") - quantity)

        if updated_count == 1:
            product = ProductModel.objects.only("id", "price", "stock").get(pk=product_id)
            return product.id, product.price, product.stock

        try:
            product = ProductModel.objects.only("id", "stock").get(pk=product_id)
        except ProductModel.DoesNotExist as exc:
            raise ProductNotFound(product_id) from exc

        raise InsufficientStock(
            product_id=product.id,
            requested_quantity=quantity,
            available_stock=product.stock,
        )


def _is_database_busy(exc: OperationalError) -> bool:
    message = str(exc).lower()
    return "database is locked" in message or "database is busy" in message
