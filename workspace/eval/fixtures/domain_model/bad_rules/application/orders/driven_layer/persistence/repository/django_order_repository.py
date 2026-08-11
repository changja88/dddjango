from __future__ import annotations

from django.core.cache import cache


class DjangoOrderRepository:
    def get_for_update(self, order_id: str) -> object:
        cached = cache.get(order_id)
        if cached is not None:
            return cached
        return self._model.objects.select_for_update().get(pk=order_id)
