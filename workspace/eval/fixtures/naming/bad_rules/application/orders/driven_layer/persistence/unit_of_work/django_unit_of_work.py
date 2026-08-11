from __future__ import annotations


class OrdersUnitOfWork:
    def after_commit(self, callback: object) -> None:
        return None
