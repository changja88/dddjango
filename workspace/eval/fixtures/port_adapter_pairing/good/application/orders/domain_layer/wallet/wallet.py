from __future__ import annotations

from application.orders.domain_layer.wallet.event.wallet_charged import WalletCharged


class Wallet:
    def __init__(self, wallet_id: str) -> None:
        self.wallet_id: str = wallet_id
        self._pending_events: list = []

    def charge(self, amount: int) -> None:
        self._amount: int = amount
        self._pending_events.append(WalletCharged())

    @property
    def has_pending_events(self) -> bool:
        return bool(self._pending_events)

    def pull_events(self) -> tuple:
        drained: tuple = tuple(self._pending_events)
        self._pending_events.clear()
        return drained
