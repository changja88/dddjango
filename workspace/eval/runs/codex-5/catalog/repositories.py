from django.db.models import QuerySet

from catalog.models import Product


class ProductNotFound(Exception):
    pass


class StockReservationConflict(Exception):
    pass


class DjangoProductRepository:
    def get_for_reservation(self, product_id: int) -> Product:
        try:
            return Product.objects.select_for_update().get(pk=product_id)
        except Product.DoesNotExist as exc:
            raise ProductNotFound from exc

    def save_reserved(self, product: Product) -> None:
        product_rows: QuerySet[Product] = Product.objects.filter(
            pk=product.pk,
            version=product.version,
        )
        updated_count = product_rows.update(
            stock=product.stock,
            version=product.version + 1,
        )
        if updated_count != 1:
            raise StockReservationConflict("Product was changed by another reservation.")

        product.version += 1
