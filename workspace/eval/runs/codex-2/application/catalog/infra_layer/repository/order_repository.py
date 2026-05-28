from django.db import OperationalError

from application.catalog.domain_layer.order.order import Order
from application.catalog.domain_layer.product.exception import DatabaseBusy
from application.catalog.infra_layer.django_catalog.models.order_model import OrderModel


class DjangoOrderRepository:
    def save(self, order: Order) -> int:
        try:
            order_model = OrderModel.objects.create(
                product_id=order.product_id,
                quantity=order.quantity,
                unit_price=order.unit_price,
            )
        except OperationalError as exc:
            if _is_database_busy(exc):
                raise DatabaseBusy("Database is temporarily busy.") from exc
            raise

        return order_model.id


def _is_database_busy(exc: OperationalError) -> bool:
    message = str(exc).lower()
    return "database is locked" in message or "database is busy" in message

