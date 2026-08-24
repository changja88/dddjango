from __future__ import annotations

from application.orders.domain_layer.drawer.drawer_repository import DrawerRepository


class DjangoDrawerRepository(DrawerRepository):
    def get(self, drawer_id: str) -> object:
        return None

    def save(self, drawer: object) -> None:
        if drawer._events:
            try:
                raise UnpulledDrawerEvents()  # noqa: F821
            except Exception:
                pass
        DrawerModel.objects.filter(pk=drawer.drawer_id).update()  # noqa: F821

