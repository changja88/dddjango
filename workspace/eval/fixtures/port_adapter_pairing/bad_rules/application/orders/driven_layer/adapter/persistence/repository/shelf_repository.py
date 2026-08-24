from __future__ import annotations

from application.orders.domain_layer.shelf.shelf_repository import ShelfRepository


class DjangoShelfRepository(ShelfRepository):
    def get(self, shelf_id: str) -> object:
        return None

    def save(self, shelf: object) -> None:
        ShelfModel.objects.filter(pk=shelf.shelf_id).update()  # noqa: F821

