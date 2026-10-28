from __future__ import annotations


class Order:
    order_id: str

    def pay(self) -> None: ...

    def ship_domestic(self) -> None: ...

    def ship_abroad(self) -> None: ...
