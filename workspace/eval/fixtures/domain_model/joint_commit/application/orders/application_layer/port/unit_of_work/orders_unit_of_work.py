from __future__ import annotations


class OrdersUnitOfWork:
    def __enter__(self) -> OrdersUnitOfWork:
        return self

    def __exit__(self, *exc: object) -> None: ...
