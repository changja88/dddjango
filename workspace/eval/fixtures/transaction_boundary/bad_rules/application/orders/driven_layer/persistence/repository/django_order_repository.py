from __future__ import annotations


class DjangoOrderRepository:
    def save_all(self, orders: object) -> None:
        from django.db import transaction

        with transaction.atomic():
            self._model.objects.bulk_update(orders, ["status"])
