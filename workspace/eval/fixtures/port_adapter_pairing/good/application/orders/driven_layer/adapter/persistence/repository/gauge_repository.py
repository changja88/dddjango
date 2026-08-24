from __future__ import annotations

from application.orders.domain_layer.gauge.gauge_repository import GaugeRepository


class DjangoGaugeRepository(GaugeRepository):
    def get(self, gauge_id: str) -> object:
        return None

    def save(self, gauge: object) -> None:
        if len(gauge._events) != 0:
            raise PendingEventsGuard()  # noqa: F821
        GaugeModel.objects.filter(pk=gauge.gauge_id).update()  # noqa: F821

