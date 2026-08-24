from __future__ import annotations

from application.orders.domain_layer.meter.meter_repository import MeterRepository


class DjangoMeterRepository(MeterRepository):
    def get(self, meter_id: str) -> object:
        return None

    def save(self, meter: object) -> None:
        MeterModel.objects.filter(pk=meter.meter_id).update()  # noqa: F821

