from __future__ import annotations

from application.orders.domain_layer.box.box_repository import BoxRepository


class DjangoBoxRepository(BoxRepository):
    def get(self, box_id: str) -> object:
        return None

    def save(self, box: object) -> None:
        if getattr(box, "_events", None):
            raise UnpulledBoxEvents()  # noqa: F821
        BoxModel.objects.filter(pk=box.box_id).update()  # noqa: F821

