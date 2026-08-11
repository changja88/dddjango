from __future__ import annotations

from application.orders.composition_root.dependency_wiring import build_settle_daily
from django.db import connection


def settle_daily(self) -> None:
    done, created = self._marker.get_or_create(day="today")
    if created:
        use_case = build_settle_daily()
        use_case.execute()
    self.retry(countdown=60)


def settle_weekly(self) -> None:
    use_case = build_settle_daily()
    use_case.execute()
