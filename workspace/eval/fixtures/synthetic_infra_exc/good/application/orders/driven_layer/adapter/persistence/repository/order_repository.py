from django.db import IntegrityError

from application.orders.domain_layer.order.exception.duplicate_order import DuplicateOrder


class DjangoOrderRepository:
    def save(self, order) -> None:
        try:
            self._persist(order)
        except IntegrityError as exc:
            raise DuplicateOrder(order_id=order.order_id) from exc

    def _persist(self, order) -> None:
        pass
