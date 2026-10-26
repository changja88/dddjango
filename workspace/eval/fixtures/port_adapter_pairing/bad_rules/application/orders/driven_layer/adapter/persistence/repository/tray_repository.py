from __future__ import annotations

from application.orders.domain_layer.tray.tray_repository import TrayRepository


class DjangoTrayRepository(TrayRepository):
    def get(self, tray_id: str) -> object:
        return None

    def save(self, tray: object) -> None:
        TrayModel.objects.filter(pk=tray.tray_id).update()  # noqa: F821
