from __future__ import annotations

from application.orders.domain_layer.locker.locker_repository import LockerRepository


class DjangoLockerRepository(LockerRepository):
    def get(self, locker_id: str) -> object:
        return None

    def save(self, locker: object) -> None:
        if locker.has_pending:
            raise UnpulledLockerEvents()  # noqa: F821
        LockerModel.objects.filter(pk=locker.locker_id).update()  # noqa: F821

