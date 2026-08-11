from __future__ import annotations

from django.db import transaction


class DjangoBillingUnitOfWork:
    def after_commit(self, callback: object) -> None:
        transaction.on_commit(callback)
