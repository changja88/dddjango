from __future__ import annotations


class DjangoOrdersUnitOfWork:
    def after_commit(self, callback: object) -> None:
        self._pending.append(callback)
