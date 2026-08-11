from __future__ import annotations

from application.orders.composition_root.dependency_wiring import build_settle_daily


def settle_daily() -> None:
    use_case = build_settle_daily()
    use_case.execute()
