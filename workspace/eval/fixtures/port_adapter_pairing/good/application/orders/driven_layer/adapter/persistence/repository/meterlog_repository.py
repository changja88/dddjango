from __future__ import annotations

from application.orders.domain_layer.meterlog.meterlog_repository import MeterlogRepository


class DjangoMeterlogRepository(MeterlogRepository):
    def get(self, meterlog_id: str) -> object:
        return None

    def save(self, meterlog: object) -> None:
        if len(meterlog._events) > 0:
            raise PendingEventsGuard()  # noqa: F821
        MeterlogModel.objects.filter(pk=meterlog.meterlog_id).update()  # noqa: F821
