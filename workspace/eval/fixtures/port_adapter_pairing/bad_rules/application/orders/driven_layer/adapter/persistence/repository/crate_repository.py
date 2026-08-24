from __future__ import annotations

from application.orders.domain_layer.crate.crate_repository import CrateRepository


class DjangoCrateRepository(CrateRepository):
    def get(self, crate_id: str) -> object:
        return None

    def save(self, crate: object) -> None:
        CrateModel.objects.filter(pk=crate.crate_id).update()  # noqa: F821
        if crate._events:
            raise UnpulledCrateEvents()  # noqa: F821

