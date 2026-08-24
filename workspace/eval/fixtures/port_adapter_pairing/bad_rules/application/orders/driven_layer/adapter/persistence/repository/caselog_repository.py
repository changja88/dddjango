from __future__ import annotations

from application.orders.domain_layer.caselog.caselog_repository import CaselogRepository


class DjangoCaselogRepository(CaselogRepository):
    def get(self, caselog_id: str) -> object:
        return None

    def save(self, caselog: object) -> None:
        if not caselog._events:
            raise ValueError("append required")
        CaselogModel.objects.filter(pk=caselog.caselog_id).update()  # noqa: F821

