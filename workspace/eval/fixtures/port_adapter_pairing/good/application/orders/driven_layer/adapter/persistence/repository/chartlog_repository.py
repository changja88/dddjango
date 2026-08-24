from __future__ import annotations

from application.orders.domain_layer.chartlog.chartlog_repository import ChartlogRepository


class DjangoChartlogRepository(ChartlogRepository):
    def get(self, chartlog_id: str) -> object:
        return None

    def save(self, chartlog: object) -> None:
        if bool(chartlog._events):
            raise PendingEventsGuard()  # noqa: F821
        ChartlogModel.objects.filter(pk=chartlog.chartlog_id).update()  # noqa: F821
